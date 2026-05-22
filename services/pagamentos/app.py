"""Serviço de Pagamentos — Loja Veloz"""
import json, os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("PORT", 8082))

class PagamentosHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[pagamentos] {fmt % args}")

    def _respond(self, code, body):
        payload = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(payload))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/health":
            self._respond(200, {"status": "ok", "service": "pagamentos"})
        else:
            self._respond(404, {"error": "Rota não encontrada"})

    def do_POST(self):
        if self.path == "/pagamentos":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or "{}")
            # Simulação de integração com gateway externo
            resultado = {"pedido_id": body.get("pedido_id"), "status": "APROVADO", "gateway": "sandbox"}
            self._respond(200, resultado)
        else:
            self._respond(404, {"error": "Rota não encontrada"})

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), PagamentosHandler)
    print(f"[pagamentos] Rodando na porta {PORT}")
    server.serve_forever()
