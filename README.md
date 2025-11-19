# Microservices + DevOps Assignment

This project implements two microservices that provide currency exchange rate data, demonstrating microservice architecture, Docker containerization, service-to-service communication, and CI/CD practices.

## Project Overview

The system consists of two microservices:

1. **currency-report**: Provides current exchange rate quotes
2. **currency-history**: Provides historical exchange rate data by calling currency-report

### Key Features

- ✅ **Microservice Architecture**: Two independent services with clear responsibilities
- ✅ **Inter-Service Communication**: currency-history calls currency-report using service names (not localhost)
- ✅ **Docker Containerization**: Both services fully containerized
- ✅ **Docker Compose Orchestration**: Services managed with compose, sharing a common network
- ✅ **CI/CD Pipeline**: GitHub Actions for automated build, test, and Docker image creation
- ✅ **Health Checks**: Both services implement health endpoints
- ✅ **Graceful Degradation**: currency-history handles currency-report unavailability

## Architecture

```
┌─────────────────────┐
│  currency-history   │
│   (Port 8101)       │
│                     │
│  GET /health        │
│  GET /history       │
└──────────┬──────────┘
           │
           │ HTTP Call
           │ (service name: currency-report:8100)
           ▼
┌─────────────────────┐
│  currency-report    │
│   (Port 8100)       │
│                     │
│  GET /health        │
│  GET /quote         │
└─────────────────────┘
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [uv](https://docs.astral.sh/uv/) (for local development)
- Python 3.12+ (for local development)

## Getting Started

### 1. Start the Environment

```bash
docker compose up --build
```

This command will:
- Build both Docker images
- Start both services
- Create a shared network for inter-service communication
- Wait for currency-report to be healthy before starting currency-history

### 2. Test the Services

Once the services are running, test them using `curl`:

#### Test currency-report

```bash
# Health check
curl http://localhost:8100/health

# Get exchange rate quote
curl "http://localhost:8100/quote?from=USD&to=BRL"

# Try different currency pairs
curl "http://localhost:8100/quote?from=EUR&to=BRL"
```

#### Test currency-history

```bash
# Health check
curl http://localhost:8101/health

# Get exchange rate history
curl "http://localhost:8101/history?from=USD&to=BRL"

# Try different currency pairs
curl "http://localhost:8101/history?from=EUR&to=BRL"
```

### 3. Stop the Environment

```bash
docker compose down
```

## API Documentation

### currency-report Service (Port 8100)

#### `GET /health`
Returns the service health status.

**Response:**
```json
{
  "status": "UP"
}
```

#### `GET /quote?from={currency}&to={currency}`
Returns the current exchange rate for a currency pair.

**Parameters:**
- `from`: Source currency code (e.g., USD, EUR)
- `to`: Target currency code (e.g., BRL)

**Response:**
```json
{
  "from": "USD",
  "to": "BRL",
  "price": 5.42,
  "timestamp": "2025-11-19T10:30:00Z"
}
```

### currency-history Service (Port 8101)

#### `GET /health`
Returns the service health status.

**Response:**
```json
{
  "status": "UP"
}
```

#### `GET /history?from={currency}&to={currency}`
Returns historical exchange rates for a currency pair, including the current rate fetched from currency-report.

**Parameters:**
- `from`: Source currency code (e.g., USD, EUR)
- `to`: Target currency code (e.g., BRL)

**Response:**
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

**Note:** The last entry is fetched in real-time from currency-report service.

## Inter-Service Communication

The currency-history service demonstrates proper microservice communication by:

1. Using the **service name** (`currency-report`) instead of localhost
2. Using the configured environment variable `CURRENCY_REPORT_URL`
3. Making async HTTP calls using `httpx.AsyncClient`
4. Implementing graceful degradation when currency-report is unavailable

```python
# Example from currency-history/src/app.py
CURRENCY_REPORT_URL = os.getenv("CURRENCY_REPORT_URL", "http://currency-report:8100")

async with httpx.AsyncClient() as client:
    response = await client.get(
        f"{CURRENCY_REPORT_URL}/quote",
        params={"from": from_currency, "to": to_currency}
    )
```

## Development

### Local Development Setup

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
# Set the service URL for local testing
export CURRENCY_REPORT_URL=http://localhost:8100
uv run uvicorn src.app:app --reload --port 8101
```

### Running Tests

#### Test currency-report

```bash
cd currency-report
uv run pytest tests/ -v
```

#### Test currency-history

```bash
cd currency-history
uv run pytest tests/ -v
```

### Building Docker Images Individually

```bash
# Build currency-report
docker build -t currency-report:latest ./currency-report

# Build currency-history
docker build -t currency-history:latest ./currency-history
```

## CI/CD Pipeline

The project includes a GitHub Actions pipeline (`.github/workflows/ci.yml`) that automatically:

1. **Builds** both services
2. **Tests** both services using pytest
3. **Creates Docker images** for both services

The pipeline runs on:
- Push to `main` or `master` branches
- Pull requests to `main` or `master` branches

Each service has its own job that runs in parallel:
- `build-test-currency-report`
- `build-test-currency-history`

## Project Structure

```
eng-sof/
├── currency-report/
│   ├── src/
│   │   └── app.py              # FastAPI application
│   ├── tests/
│   │   └── test_app.py         # Unit tests
│   ├── Dockerfile              # Container configuration
│   └── pyproject.toml          # Python dependencies
├── currency-history/
│   ├── src/
│   │   └── app.py              # FastAPI application
│   ├── tests/
│   │   └── test_app.py         # Unit tests (with mocked inter-service calls)
│   ├── Dockerfile              # Container configuration
│   └── pyproject.toml          # Python dependencies
├── .github/
│   └── workflows/
│       └── ci.yml              # CI/CD pipeline
├── compose.yaml                # Docker Compose configuration
└── README.md                   # This file
```

## Technology Stack

- **Language**: Python 3.12+
- **Web Framework**: FastAPI
- **ASGI Server**: Uvicorn
- **HTTP Client**: httpx (async)
- **Testing**: pytest
- **Package Manager**: uv
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **CI/CD**: GitHub Actions

## Design Decisions

### Why FastAPI?
- Modern, fast Python web framework
- Built-in async support for inter-service communication
- Automatic OpenAPI documentation
- Type hints and validation with Pydantic

### Why uv?
- Fast, modern Python package manager
- Excellent for reproducible builds
- Simple dependency management

### Why Docker Compose?
- Easy orchestration of multiple services
- Built-in networking for service discovery
- Health checks and dependency management
- Perfect for development and testing

### Mocked Data
The services use mocked exchange rate data to keep the implementation simple and avoid external API dependencies. In production, these would connect to real exchange rate APIs.

## Troubleshooting

### Services won't start
```bash
# Check if ports are already in use
lsof -i :8100
lsof -i :8101

# Check Docker logs
docker compose logs currency-report
docker compose logs currency-history
```

### currency-history can't reach currency-report
- Ensure both services are on the same Docker network
- Check that `CURRENCY_REPORT_URL` uses the service name (`currency-report`)
- Verify currency-report's health check is passing

### Tests failing
```bash
# Ensure you've installed dev dependencies
uv sync --extra dev

# Run tests with verbose output
uv run pytest tests/ -v -s
```

## Future Enhancements

- [ ] Add database for persistent historical data
- [ ] Integrate with real exchange rate APIs
- [ ] Add authentication and rate limiting
- [ ] Implement caching layer (Redis)
- [ ] Add monitoring and observability (Prometheus, Grafana)
- [ ] Deploy to Kubernetes
- [ ] Add more comprehensive error handling and logging

## License

This is an educational project for a DevOps assignment.

## Authors

Created as part of the Software Engineering undergraduate program.

