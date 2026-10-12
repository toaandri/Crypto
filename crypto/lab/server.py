"""Loopback-only HTTP server for Crypto Lab, with no third-party dependencies."""

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from importlib.resources import files
import json
import socket
from urllib.parse import urlsplit
import webbrowser

from .service import run_experiment

MAX_BODY = 16384
ASSETS = {"/": ("index.html", "text/html; charset=utf-8"),
          "/style.css": ("style.css", "text/css; charset=utf-8"),
          "/app.js": ("app.js", "text/javascript; charset=utf-8"),
          "/favicon.svg": ("favicon.svg", "image/svg+xml")}


class LabHandler(BaseHTTPRequestHandler):
    server_version = "CryptoLab/1.1"

    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def _allowed_host(self):
        port = self.server.server_address[1]
        return self.headers.get("Host") in (f"127.0.0.1:{port}", f"localhost:{port}")

    def _reply(self, status, body, content_type="application/json; charset=utf-8"):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; script-src 'self'; style-src 'self'; "
                         "img-src 'self'; connect-src 'self'; base-uri 'none'; "
                         "frame-ancestors 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self._allowed_host():
            return self._reply(403, {"error": "A local host is required."})
        path = urlsplit(self.path).path
        if path == "/api/health":
            return self._reply(200, {"status": "ok", "educational_only": True})
        asset = ASSETS.get(path)
        if asset is None:
            return self._reply(404, {"error": "Page not found."})
        name, content_type = asset
        self._reply(200, files("crypto.lab").joinpath("static", name).read_bytes(), content_type)

    def do_POST(self):
        port = self.server.server_address[1]
        origins = (f"http://127.0.0.1:{port}", f"http://localhost:{port}")
        if (not self._allowed_host() or self.headers.get("Origin") not in (None, *origins)
                or self.headers.get("X-Crypto-Lab") != "1"):
            return self._reply(403, {"error": "Open the lab from its local address."})
        if self.path != "/api/run":
            return self._reply(404, {"error": "Operation not found."})
        if (self.headers.get("Content-Type", "").split(";", 1)[0].strip() != "application/json"
                or self.headers.get("Transfer-Encoding") is not None):
            return self._reply(415, {"error": "Use a JSON request with Content-Length."})
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self._reply(400, {"error": "Invalid request size."})
        if not 0 < length <= MAX_BODY:
            return self._reply(413, {"error": "The request must contain at most 16 KiB."})
        try:
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise ValueError("Incomplete request.")
            request = json.loads(raw)
            result = run_experiment(request)
        except (ValueError, TypeError, UnicodeError, RecursionError) as error:
            return self._reply(400, {"error": str(error) or "Invalid parameters."})
        except (socket.timeout, OSError):
            return self._reply(408, {"error": "Request read timed out."})
        self._reply(200, result)

    def log_message(self, format, *args):
        # Keep message/key input out of server logs.
        pass


def make_server(port=8000):
    """Create an IPv4 loopback server. Port 0 selects an available port."""
    return HTTPServer(("127.0.0.1", port), LabHandler)


def main():
    parser = argparse.ArgumentParser(description="Open the educational Crypto Lab locally.")
    parser.add_argument("--port", type=int, default=8000, help="local port (default: 8000; 0: automatic)")
    parser.add_argument("--open", action="store_true", help="open your default browser")
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("port must be between 0 and 65535")
    try:
        server = make_server(args.port)
    except OSError as error:
        parser.exit(1, f"Cannot start Crypto Lab: {error}\nTry --port 8001.\n")
    with server:
        url = f"http://127.0.0.1:{server.server_address[1]}"
        print(f"Crypto Lab: {url}\nEducational algorithms only. Press Ctrl+C to stop.", flush=True)
        if args.open:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nCrypto Lab stopped.")
