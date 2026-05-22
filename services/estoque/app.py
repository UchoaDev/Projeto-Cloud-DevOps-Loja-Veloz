"""Serviço de Estoque — Loja Veloz"""
import json, os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("PORT", 8083))
ESTOQUE = {"produto-001": 100, "produto-002": 50}

class EstoqueHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[estoque] {fmt % args}")

    def _respond(self, code, body):
        payload = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(payload))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/health":
            self._respond(200, {"status": "ok", "service": "estoque"})
        elif self.path == "/estoque":
            self._respond(200, ESTOQUE)
        else:
            self._respond(404, {"error": "Rota não encontrada"})

    def do_POST(self):
        if self.path == "/estoque/reservar":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or "{}")
            produto = body.get("produto_id")
            qtd = body.get("quantidade", 1)
            if ESTOQUE.get(produto, 0) >= qtd:
                ESTOQUE[produto] -= qtd
                self._respond(200, {"reservado": True, "saldo": ESTOQUE[produto]})
            else:
                self._respond(409, {"reservado": False, "error": "Estoque insuficiente"})
        else:
            self._respond(404, {"error": "Rota não encontrada"})

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), EstoqueHandler)
    print(f"[estoque] Rodando na porta {PORT}")
    server.serve_forever()
