# Trabalho Eng Soft II - Roberto Martins

Este projeto implementa dois microserviços que fornecem dados de taxa de câmbio, demonstrando arquitetura de microserviços, containerização com Docker, comunicação entre serviços e práticas de CI/CD.

## Visão Geral do Projeto

O sistema consiste em dois microserviços:

1. **currency-report**: Fornece cotações atuais de taxas de câmbio
2. **currency-history**: Fornece dados históricos de taxas de câmbio chamando o currency-report

### Funcionalidades Principais

- ✅ **Arquitetura de Microserviços**: Dois serviços independentes com responsabilidades claras
- ✅ **Comunicação Entre Serviços**: currency-history chama currency-report usando nomes de serviço (não localhost)
- ✅ **Containerização com Docker**: Ambos os serviços totalmente containerizados
- ✅ **Orquestração com Docker Compose**: Serviços gerenciados com compose, compartilhando uma rede comum
- ✅ **Pipeline CI/CD**: GitHub Actions para build, teste e criação de imagens Docker automatizados
- ✅ **Health Checks**: Ambos os serviços implementam endpoints de saúde
- ✅ **Degradação Graceful**: currency-history trata a indisponibilidade do currency-report

## Arquitetura

```
┌─────────────────────┐
│  currency-history   │
│   (Porta 8101)      │
│                     │
│  GET /health        │
│  GET /history       │
└──────────┬──────────┘
           │
           │ Chamada HTTP
           │ (nome do serviço: currency-report:8100)
           ▼
┌─────────────────────┐
│  currency-report    │
│   (Porta 8100)      │
│                     │
│  GET /health        │
│  GET /quote         │
└─────────────────────┘
```

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [uv](https://docs.astral.sh/uv/) (para desenvolvimento local)
- Python 3.12+ (para desenvolvimento local)

## Como Começar

### 1. Iniciar o Ambiente

```bash
docker compose up --build
```

Este comando irá:
- Construir ambas as imagens Docker
- Iniciar ambos os serviços
- Criar uma rede compartilhada para comunicação entre serviços
- Aguardar o currency-report estar saudável antes de iniciar o currency-history

### 2. Testar os Serviços

Uma vez que os serviços estejam rodando, teste-os usando `curl`:

#### Testar currency-report

```bash
# Health check
curl http://localhost:8100/health

# Obter cotação de taxa de câmbio
curl "http://localhost:8100/quote?from=USD&to=BRL"

# Tentar diferentes pares de moedas
curl "http://localhost:8100/quote?from=EUR&to=BRL"
```

#### Testar currency-history

```bash
# Health check
curl http://localhost:8101/health

# Obter histórico de taxa de câmbio
curl "http://localhost:8101/history?from=USD&to=BRL"

# Tentar diferentes pares de moedas
curl "http://localhost:8101/history?from=EUR&to=BRL"
```

### 3. Parar o Ambiente

```bash
docker compose down
```

## Documentação da API

### Serviço currency-report (Porta 8100)

#### `GET /health`
Retorna o status de saúde do serviço.

**Resposta:**
```json
{
  "status": "UP"
}
```

#### `GET /quote?from={moeda}&to={moeda}`
Retorna a taxa de câmbio atual para um par de moedas.

**Parâmetros:**
- `from`: Código da moeda de origem (ex: USD, EUR)
- `to`: Código da moeda de destino (ex: BRL)

**Resposta:**
```json
{
  "from": "USD",
  "to": "BRL",
  "price": 5.42,
  "timestamp": "2025-11-19T10:30:00Z"
}
```

### Serviço currency-history (Porta 8101)

#### `GET /health`
Retorna o status de saúde do serviço.

**Resposta:**
```json
{
  "status": "UP"
}
```

#### `GET /history?from={moeda}&to={moeda}`
Retorna taxas de câmbio históricas para um par de moedas, incluindo a taxa atual obtida do currency-report.

**Parâmetros:**
- `from`: Código da moeda de origem (ex: USD, EUR)
- `to`: Código da moeda de destino (ex: BRL)

**Resposta:**
```json
{
  "from": "USD",
  "to": "BRL",
  "values": [
    {
      "timestamp": "2025-11-16T10:30:00Z",
      "price": 5.38
    },
    {
      "timestamp": "2025-11-17T10:30:00Z",
      "price": 5.40
    },
    {
      "timestamp": "2025-11-18T10:30:00Z",
      "price": 5.41
    },
    {
      "timestamp": "2025-11-19T10:30:00Z",
      "price": 5.42
    }
  ]
}
```

**Nota:** A última entrada é obtida em tempo real do serviço currency-report.

## Desenvolvimento

### Configuração de Desenvolvimento Local

#### currency-report

```bash
cd currency-report
uv sync --extra dev
uv run uvicorn src.app:app --reload --port 8100
```

#### currency-history

```bash
cd currency-history
uv sync --extra dev
# Definir a URL do serviço para testes locais
export CURRENCY_REPORT_URL=http://localhost:8100
uv run uvicorn src.app:app --reload --port 8101
```

### Executar Testes

#### Testar currency-report

```bash
cd currency-report
uv run pytest tests/ -v
```

#### Testar currency-history

```bash
cd currency-history
uv run pytest tests/ -v
```

### Construir Imagens Docker Individualmente

```bash
# Construir currency-report
docker build -t currency-report:latest ./currency-report

# Construir currency-history
docker build -t currency-history:latest ./currency-history
```

## Pipeline CI/CD

O projeto inclui um pipeline do GitHub Actions (`.github/workflows/ci.yml`) que automaticamente:

1. **Constrói** ambos os serviços
2. **Testa** ambos os serviços usando pytest
3. **Cria imagens Docker** para ambos os serviços

O pipeline é executado em:
- Push para as branches `main` ou `master`
- Pull requests para as branches `main` ou `master`

Cada serviço tem seu próprio job que roda em paralelo:
- `build-test-currency-report`
- `build-test-currency-history`

## Estrutura do Projeto

```
eng-sof/
├── currency-report/
│   ├── src/
│   │   └── app.py              # Aplicação FastAPI
│   ├── tests/
│   │   └── test_app.py         # Testes unitários
│   ├── Dockerfile              # Configuração do container
│   └── pyproject.toml          # Dependências Python
├── currency-history/
│   ├── src/
│   │   └── app.py              # Aplicação FastAPI
│   ├── tests/
│   │   └── test_app.py         # Testes unitários (com chamadas entre serviços mockadas)
│   ├── Dockerfile              # Configuração do container
│   └── pyproject.toml          # Dependências Python
├── .github/
│   └── workflows/
│       └── ci.yml              # Pipeline CI/CD
├── compose.yaml                # Configuração do Docker Compose
└── README.md                   # Este arquivo
```

## Solução de Problemas

### Serviços não iniciam
```bash
# Verificar se as portas já estão em uso
lsof -i :8100
lsof -i :8101

# Verificar logs do Docker
docker compose logs currency-report
docker compose logs currency-history
```

### currency-history não consegue alcançar currency-report
- Garantir que ambos os serviços estão na mesma rede Docker
- Verificar que `CURRENCY_REPORT_URL` usa o nome do serviço (`currency-report`)
- Verificar se o health check do currency-report está passando

### Testes falhando
```bash
# Garantir que você instalou as dependências de dev
uv sync --extra dev

# Executar testes com saída verbosa
uv run pytest tests/ -v -s
```
