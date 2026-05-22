/**
 * API Gateway — Loja Veloz
 * Responsável por rotear requisições para os microsserviços internos.
 */
const http = require("http");
const url = require("url");

const PORT = process.env.PORT || 8080;

const SERVICES = {
  "/pedidos": process.env.PEDIDOS_URL || "http://pedidos:8081",
  "/pagamentos": process.env.PAGAMENTOS_URL || "http://pagamentos:8082",
  "/estoque": process.env.ESTOQUE_URL || "http://estoque:8083",
};

function proxy(req, res, targetBase) {
  const target = new url.URL(req.url, targetBase);
  const options = {
    hostname: target.hostname,
    port: target.port || 80,
    path: target.pathname + (target.search || ""),
    method: req.method,
    headers: { ...req.headers, host: target.hostname },
  };

  const proxyReq = http.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res, { end: true });
  });

  proxyReq.on("error", (err) => {
    console.error(`[gateway] Erro ao conectar ao serviço: ${err.message}`);
    res.writeHead(502);
    res.end(JSON.stringify({ error: "Bad Gateway", detail: err.message }));
  });

  req.pipe(proxyReq, { end: true });
}

const server = http.createServer((req, res) => {
  // Health check do próprio gateway
  if (req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok", service: "api-gateway" }));
    return;
  }

  // Roteamento para microsserviços
  for (const [prefix, target] of Object.entries(SERVICES)) {
    if (req.url.startsWith(prefix)) {
      console.log(`[gateway] ${req.method} ${req.url} → ${target}`);
      return proxy(req, res, target);
    }
  }

  // Rota não encontrada
  res.writeHead(404, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ error: "Not Found" }));
});

server.listen(PORT, () => {
  console.log(`[api-gateway] Rodando na porta ${PORT}`);
});
