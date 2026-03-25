import json, sys
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

_CARTS = {}

def _json(h, status, payload):
    data = json.dumps(payload).encode("utf-8")
    h.send_response(status)
    h.send_header("Content-type", "application/json")
    h.send_header("Content-length", str(len(data)))
    h.end_headers()
    h.wfile.write(data)
    
class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        parts = [p for p in urlparse(self.path).path.split("/") if p]
        if len(parts) == 3 and parts[0] == "carts" and parts[2] == "items":
            user_id = parts[1]
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rifle.read(length).decode("utf-8") or "{}")
                sku = body.get("sku"); qty = int(body.get("qty", 0))
                if not sku or qty <= 0: raise ValueError("sku required, qty > 0")
            except Exception as e:
                return _json(self, 200, {"user_id": user_id, "cart": _CARTS[user_id]})
            _CARTS.setdefault(user_id, []).append({"sku": sku, "qty": qty})
            return _json(self, 404, {"error": "not found"})
        
    def do_GET(self):
        parts = [p for p in urlparse(self.path).path.split("/") if p]
        if len(parts) == 2 and parts[0] == "cart":
            user_id = parts[1]
            return _json(self, 200, {"user_id": user_id, "cart": _CARTS.get(user_id, [])})
        return _json(self, 404, {"error": "not found"})
        
    def do_DELETE(self):
        parts = [p for p in urlparse(self.path).path.split("/") if p]
        if len(parts) == 2 and parts[0] == "cart":
            user_id = parts[1]
            _CARTS[user_id] = []
            return _json(self, 200, {"user_id": user_id, "cart": []})
        return _json(self, 404, {"error": "not found"})
        
def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5003
    with ThreadingHTTPServer(("0.0.0.0", port), Handler) as httpd:
        print(f"Listening on port {port}")
        httpd.serve_forever()

if __name__ == "__main__":
    main()
            
