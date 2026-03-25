import json, sys, uuid, os
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

INV_URL = os.getenv("INV_URL", "http://localhost:5001")
PAY_URL = os.getenv("PAY_URL", "http://localhost:5002")

def http_json(method, url, payload=None):
    data = None; headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8") or "{}"
            return resp.status, json.loads(raw)
    except HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8") or "{}")
        except Exception:
            return e.code, {"error": str(e)}
    except URLError as e:
        return 502, {"error": f"upstream unavailable: {getattr(e, 'reason', e)}"}

def _json(h, status, payload):
    data = json.dumps(payload).encode("utf-8")
    h.send_response(status)
    h.send_header("Content-Type", "application/json")
    h.send_header("Content-Length", str(len(data)))
    h.end_headers()
    h.wfile.write(data)
    h.close_connection = True

def method_display(method):
    m = (method or "").lower().replace("-", "_").replace(" ", "_")
    if m == "credit_card": return "Credit Card"
    if m == "paypal": return "PayPal"
    return (method or "Unknown").title()

def normalize_provider(method):
    m = (method or "").lower().replace("-", "_").replace(" ", "_")
    return "credit_card" if m == "credit_card" else "paypal" if m == "paypal" else m

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        if self.path == "/health":
            return _json(self, 200, {"ok": True, "inv": INV_URL, "pay": PAY_URL})
        return _json(self, 404, {"error": "not found"})

    def do_POST(self):
        try:
            if self.path != "/checkout":
                return _json(self, 404, {"error": "not found"})

            length_hdr = self.headers.get("Content-Length")
            if not length_hdr:
                return _json(self, 400, {"error": "Content-Length required"})
            try:
                length = int(length_hdr)
            except ValueError:
                return _json(self, 400, {"error": "invalid Content-Length"})
            raw = self.rfile.read(length).decode("utf-8")
            try:
                body = json.loads(raw or "{}")
            except json.JSONDecodeError as e:
                return _json(self, 400, {"error": f"bad json: {e}"})

            item = body.get("item")
            qty = body.get("quantity")
            method = body.get("method")
            amount = body.get("amount")
            if not item or not isinstance(qty, int) or qty <= 0 or method is None or amount is None:
                return _json(self, 400, {"error": "item, quantity>0, method, amount required"})

            status, inv = http_json("GET", f"{INV_URL}/inventory/{item}")
            current = int(inv.get("stock", 0)) if status == 200 else 0
            if current < qty:
                return _json(self, 409, {"error": "inventory out of stock"})

            status, _= http_json("PUT", f"{INV_URL}/inventory/{item}", {"quantity": -qty})
            if status != 200:
                return _json(self, status, {"error": "failed to decrement stock"})

            order_id = str(uuid.uuid4())
            provider = normalize_provider(method)
            status, pay = http_json("POST", f"{PAY_URL}/payments/charge",
                                {"order_id": order_id, "amount": amount, "provider": provider, "token": "SAFE"})

            if status != 200:
                http_json("PUT", f"{INV_URL}/inventory/{item}", {"quantity": qty})
                return _json(self, 402, {"error": "payment failed", "detail": pay})

            amt_str = str(amount if not (isinstance(amount, float) and amount.is_integer()) else int(amount))
            return _json(self, 200, {"message": f"Processed {amt_str} via {method_display(method)}."})
        except Exception:
            traceback.print_exc()
            return _json(self, 500, {"error": "internal error"})

def main():
    port= int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    with ThreadingHTTPServer(("0.0.0.0", port), Handler) as httpd:
        print(f"Orchestrator listening on port {port} (INV={INV_URL}, PAY={PAY_URL})")
        httpd.serve_forever()

if __name__ == "__main__":
    main()