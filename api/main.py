import http.server
import json
import os
import socket
import threading
import time

import httpx


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            body = json.dumps({
                "status": "ok",
                "service": "synapseshop-api",
            }).encode()
        else:
            body = json.dumps({
                "service": "synapseshop-api",
                "hostname": socket.gethostname(),
                "env": os.getenv("APP_ENV", "dev"),
            }).encode()
        self._send(body)

    def _send(self, body):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"[synapseshop-api] {fmt % args}", flush=True)


def self_check(port):
    while True:
        try:
            response = httpx.get(f"http://127.0.0.1:{port}/health", timeout=3)
            print(f"[synapseshop-api] healthcheck interno httpx -> {response.status_code}", flush=True)
        except Exception as exc:
            print(f"[synapseshop-api] self-check falhou -> {exc}", flush=True)
        time.sleep(15)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"[synapseshop-api] subindo em http://0.0.0.0:{port}", flush=True)
    threading.Thread(target=self_check, args=(port,), daemon=True).start()
    http.server.HTTPServer(("0.0.0.0", port), Handler).serve_forever()