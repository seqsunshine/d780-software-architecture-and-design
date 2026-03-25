import json, sys, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

_TXN = {}

def _json(h, status, payload):
    data = json.dumps(payload).encode("utf-8")
    h.send_response(status); h.send_header("Content-Type", "application/json")
    h.send_header("Content-Length", str(len(data))); h.end_headers()
    h.wfile.write(data)

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except Exception as e:
            return _json(self, 400, {"error": f"bad json: {e}"})

        if self.path == "/payments/charge":
            order_id = body.get("order_id")
            amount = body.get("amount")
            provider = (body.get("provider") or "").lower()
            token = body.get("token") or ""
            if not order_id or not provider or (not isinstance(amount, (int, float)) or amount <=0):
                return _json(self, 400, {"error": "order_id, provider, amount > 0 required"})
            if provider == "credit_card" and str(token).startswith("DECLINE"):
                return _json(self, 402, {"error": "card declined"})
            if provider == "paypal" and str(token).startswith("DECLINE"):
                return _json(self, 402, {"error": "paypal blocked"})
            txn_id = str(uuid.uuid4())
            _TXN[txn_id] = {"order_id": order_id, "amount": amount, "provider": provider, "status": "captured"}
            return _json(self, 200, {"txn_id": txn_id, "status": "captured"})
        if self.path == "/payments/refund":
            txn_id = body.get("txn_id" or "")
            if txn_id not in _TXN:
                return _json(self, 400, {"error": "unknown txn_id"})
            _TXN[txn_id]["status"] = "refunded"
            return _json(self, 200, {"txn_id": txn_id, "status": "refunded"})

        return _json(self, 4004, {"error": "not found"})

def main():
    port= int(sys.argv[1]) if len(sys.argv) > 1 else 5002
    with ThreadingHTTPServer(("0.0.0.0", port), Handler) as httpd:
        print(f"Payment listining on : {port}")
        httpd.serve_forever()

if __name__ == "__main__":
    main()