# Loja Veloz — Plataforma de Pedidos em Microsserviços

> Projeto acadêmico de Cloud DevOps — UniFECAF  
> Disciplina: Cloud DevOps: Orchestrating Containers and Microservices

## Visão Geral da Arquitetura

```
                        ┌─────────────────┐
                        │   API Gateway   │  :8080
                        │  (Node.js)      │
                        └────────┬────────┘
               ┌─────────────────┼─────────────────┐
               ▼                 ▼                 ▼
    ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
    │ Serv. de Pedidos │ │ Pagamentos   │ │ Serv. de Estoque │
    │   (Python)  8081 │ │ (Python)8082 │ │  (Python)   8083 │
    └────────┬─────────┘ └──────────────┘ └──────────────────┘
             │
    ┌────────┴────────┐          ┌────────────────┐
    │   PostgreSQL    │          │   RabbitMQ     │
    │    (port 5432)  │          │  (Mensageria)  │
    └─────────────────┘          └────────────────┘

Observabilidade:
    Prometheus :9090 | Grafana :3000 | Jaeger :16686
```

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando
- [Git](https://git-scm.com/) instalado

## Como Rodar Localmente

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/loja-veloz.git
cd loja-veloz

# 2. Copie e configure as variáveis de ambiente
cp .env.example .env
# (edite o .env se quiser mudar senhas)

# 3. Suba todos os serviços com um único comando
docker compose up --build

# 4. Verifique que tudo está rodando
docker compose ps
```

## Serviços e Portas

| Serviço       | Porta | URL                          |
|---------------|-------|------------------------------|
| API Gateway   | 8080  | http://localhost:8080        |
| Pedidos       | 8081  | http://localhost:8081/health |
| Pagamentos    | 8082  | http://localhost:8082/health |
| Estoque       | 8083  | http://localhost:8083/health |
| RabbitMQ UI   | 15672 | http://localhost:15672       |
| Prometheus    | 9090  | http://localhost:9090        |
| Grafana       | 3000  | http://localhost:3000        |
| Jaeger UI     | 16686 | http://localhost:16686       |

## Testando a API

```bash
# Health check do gateway
curl http://localhost:8080/health

# Criar um pedido
curl -X POST http://localhost:8080/pedidos \
  -H "Content-Type: application/json" \
  -d '{"cliente": "João Silva", "itens": [{"produto_id": "produto-001", "quantidade": 2}]}'

# Listar pedidos
curl http://localhost:8080/pedidos

# Verificar estoque
curl http://localhost:8080/estoque
```

## Deploy em Kubernetes

```bash
# 1. Criar namespace e configs
kubectl apply -f k8s/base/configmap-secrets.yaml

# 2. Deploy de todos os serviços
kubectl apply -f k8s/base/

# 3. Verificar pods rodando
kubectl get pods -n loja-veloz

# 4. Verificar serviços
kubectl get services -n loja-veloz
```

## CI/CD

O pipeline (`.github/workflows/ci-cd.yml`) executa automaticamente ao fazer push para `main`:

1. **Lint** — valida Dockerfiles, YAMLs e manifests K8s
2. **Testes** — roda testes unitários de cada serviço
3. **Build & Push** — constrói e publica imagens no GitHub Container Registry
4. **Deploy** — aplica manifests no cluster Kubernetes via Rolling Update

Para ativar o deploy, configure o secret `KUBECONFIG` nas configurações do repositório GitHub.

## Infraestrutura como Código (Terraform)

```bash
cd terraform
terraform init
terraform plan -var="db_username=postgres" -var="db_password=suasenha"
terraform apply
```

## Observabilidade

- **Métricas**: Prometheus coleta de todos os serviços → Grafana exibe dashboards
- **Logs**: stdout estruturado de cada container, coletado pelo log driver do Docker/K8s
- **Tracing**: Jaeger recebe spans via OpenTelemetry (OTLP)

## Vídeo Pitch

[🎥 Assistir no YouTube](https://youtube.com/SEU_LINK_AQUI)

## Estrutura do Projeto

```
loja-veloz/
├── services/
│   ├── api-gateway/     # API Gateway (Node.js)
│   ├── pedidos/         # Serviço de Pedidos (Python)
│   ├── pagamentos/      # Serviço de Pagamentos (Python)
│   └── estoque/         # Serviço de Estoque (Python)
├── k8s/
│   └── base/            # Manifests Kubernetes
├── terraform/           # Infraestrutura como Código
├── .github/workflows/   # Pipeline CI/CD (GitHub Actions)
├── ci/                  # Configurações de observabilidade
├── docker-compose.yml   # Ambiente local
└── README.md
```
