import json, sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

_INVENTORY = {"Laptop": 5}

def _json(h, status, payload):
    data = json.dumps(payload).encode("utf-8")
    h.send_response(status)
    h.send_header("Content-Type", "application/json")
    h.send_header("Content-Length", str(len(data)))
    h.end_headers()
    h.wfile.write(data)
    h.close_connection = True

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_PUT(self):
        try:
            parts = [p for p in urlparse(self.path).path.split("/") if p]
            if len(parts) == 2 and parts[0] == "inventory":
                item = parts[1]

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
                    return _json(self, 400, {"errror": f"bad json: {e}"})

                qty = body.get("quantity")
                if not isinstance(qty, int):
                    return _json(self, 400, {"error": "quantity (int) required"})

                _INVENTORY[item] = _INVENTORY.get(item, 0) + qty
                print(f"[NOTIFY] {item} stock is now {_INVENTORY[item]}.")
                return _json(self, 200, {"message": f"{item} stock updated."})

            return _json(self, 404, {"error": "not found"})
        except Exception:
            traceback.print_exc()
            return _json(self, 500, {"error": "internal server error"})

    def do_GET(self):
        try:
            parts = [p for p in urlparse(self.path).path.split("/") if p]
            if len(parts) == 2 and parts[0] == "inventory":
                item = parts[1]
                return _json(self, 200, {"item": item, "stock": _INVENTORY.get(item, 0)})
            return _json(self, 400, {"error": "not found"})
        except Exception:
            traceback.print_exc()
            return _json(self, 500, {"error": "internal server error"})

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    with ThreadingHTTPServer(("0.0.0.0", port), Handler) as httpd:
        print(f"Inventory listening on: {port}")
        httpd.serve_forever()

if __name__ == "__main__":
    main()