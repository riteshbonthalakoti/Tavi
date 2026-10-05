import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from tavi import respond

HTML_FILE = Path(__file__).resolve().parent / "index.html"

class TaviRequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/index.html", "/static/index.html"):
            if not HTML_FILE.exists():
                self.send_error(404, "index.html not found")
                return
            content = HTML_FILE.read_bytes()
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path in ("/chat", "/api/chat"):
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
                user_message = data.get("message") or data.get("text") or ""
            except Exception:
                self.send_error(400, "Invalid JSON payload")
                return

            reply = respond(user_message)
            response_bytes = json.dumps({"response": reply}).encode("utf-8")

            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(response_bytes)))
            self.end_headers()
            self.wfile.write(response_bytes)
            return

        self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        pass

def main():
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer((host, port), TaviRequestHandler)
    print(f"Tavi web server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
