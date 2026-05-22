"""
Serviço de Pedidos — Loja Veloz
Responsável por criar e consultar pedidos, persistindo no PostgreSQL
e publicando eventos no RabbitMQ.
"""
import json
import os
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("PORT", 8081))

# Simulação em memória (substituir por PostgreSQL real via psycopg2)
PEDIDOS = {}


class PedidosHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"[pedidos] {self.address_string()} - {fmt % args}")

    def _respond(self, code, body):
        payload = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(payload))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/health":
            self._respond(200, {"status": "ok", "service": "pedidos"})
        elif self.path.startswith("/pedidos/"):
            pid = self.path.split("/")[-1]
            pedido = PEDIDOS.get(pid)
            if pedido:
                self._respond(200, pedido)
            else:
                self._respond(404, {"error": "Pedido não encontrado"})
        elif self.path == "/pedidos":
            self._respond(200, list(PEDIDOS.values()))
        else:
            self._respond(404, {"error": "Rota não encontrada"})

    def do_POST(self):
        if self.path == "/pedidos":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or "{}")
            pedido_id = str(uuid.uuid4())
            pedido = {
                "id": pedido_id,
                "cliente": body.get("cliente", "desconhecido"),
                "itens": body.get("itens", []),
                "status": "CRIADO",
            }
            PEDIDOS[pedido_id] = pedido
            # TODO: publicar evento "PedidoCriado" no RabbitMQ
            print(f"[pedidos] Pedido criado: {pedido_id}")
            self._respond(201, pedido)
        else:
            self._respond(404, {"error": "Rota não encontrada"})


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), PedidosHandler)
    print(f"[pedidos] Rodando na porta {PORT}")
    server.serve_forever()
