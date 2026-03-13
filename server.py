#!/usr/bin/env python3
"""
Local proxy server for Q-SYS Reflect API Explorer.
- Serves index.html at http://localhost:8080/
- Proxies API calls: GET/POST http://localhost:8080/proxy/<path>
  → https://reflect.qsc.com/api/public/v0/<path>
This avoids CORS restrictions in the browser.
"""

import json
import urllib.request
import urllib.error
from http.server import HTTPServer, SimpleHTTPRequestHandler

REFLECT_BASE = "https://reflect.qsc.com/api/public/v0"


class ProxyHandler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"  {self.command} {self.path} → {args[1] if len(args) > 1 else ''}")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/proxy"):
            self._proxy("GET")
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/proxy"):
            self._proxy("POST")
        else:
            self.send_error(404)

    def do_PUT(self):
        if self.path.startswith("/proxy"):
            self._proxy("PUT")

    def do_DELETE(self):
        if self.path.startswith("/proxy"):
            self._proxy("DELETE")

    def _proxy(self, method):
        # Extract the API path after /proxy
        api_path = self.path[len("/proxy"):]
        if not api_path:
            api_path = "/"
        target_url = REFLECT_BASE + api_path

        # Read Authorization header from the browser request
        auth = self.headers.get("Authorization", "")
        body = None

        if method in ("POST", "PUT"):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else None

        req = urllib.request.Request(
            target_url,
            data=body,
            method=method,
            headers={
                "Authorization": auth,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self._cors()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(502)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), ProxyHandler)
    print("Q-SYS Reflect API Proxy running at http://localhost:8080")
    print("Open http://localhost:8080/index.html in your browser")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
