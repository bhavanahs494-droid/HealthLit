"""Web server. Run: python app.py  then open http://127.0.0.1:8000"""
import json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from healthlit import assistant, llm

PAGE = Path(__file__).parent / "web" / "index.html"

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, kind="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", kind + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self._send(200, PAGE.read_bytes(), "text/html")
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        routes = {"/api/ask": assistant.ask, "/api/simplify": assistant.simplify}
        if self.path not in routes:
            return self._send(404, {"error": "not found"})
        if not self.headers.get("Content-Type", "").startswith("application/json"):
            return self._send(415, {"error": "send JSON"})
        try:
            size = int(self.headers.get("Content-Length", 0))
            if not 0 < size <= 20000:
                raise ValueError
            text = json.loads(self.rfile.read(size))["text"]
            if not isinstance(text, str):
                raise ValueError
        except (ValueError, KeyError, TypeError):
            return self._send(400, {"error": "invalid request"})
        self._send(200, routes[self.path](text))

    def log_message(self, *args):  # do not log health questions or requests
        pass

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"HealthLit ({llm.provider()} mode): http://127.0.0.1:{port}  (Ctrl+C to stop)")
    try:
        ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
