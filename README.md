# Distributed Issue Tracker - FastAPI Microservices

A production-grade, cloud-native issue management platform built with FastAPI microservices architecture, inspired by Jira and Linear.

## 🏗️ Architecture Overview

This project demonstrates real-world backend system design with:

- **Microservices Architecture**: 8 independent services with clear boundaries
- **Event-Driven Architecture**: Asynchronous workflows via RabbitMQ
- **Database-per-Service Pattern**: Data isolation and ownership
- **API Gateway Pattern**: Centralized routing and authentication
- **Production Observability**: Distributed tracing, metrics, and logging

## 📊 Services

| Service | Port | Responsibility |
|---------|------|-----------------|
| API Gateway | 8000 | Request routing, TLS, rate limiting, JWT validation |
| Auth Service | 8001 | Authentication, JWT issuance, OAuth2 integration |
| User Service | 8002 | User profiles, teams, preferences |
| Project Service | 8003 | Project lifecycle, team membership |
| Issue Service | 8004 | Issue CRUD, workflow states, assignments |
| Comment Service | 8005 | Comments, mentions, edit history |
| Notification Service | 8006 | Email, in-app notifications, webhooks |
| Search Service | 8007 | Full-text search, filters, faceted queries |
| Audit Service | 8008 | Activity logs, compliance history |

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Async REST APIs
- **Uvicorn + Gunicorn** - ASGI server
- **Pydantic** - Data validation

### Data Layer
- **PostgreSQL** - Primary transactional database
- **Redis** - Caching, rate limiting, distributed locks
- **Elasticsearch** - Full-text search indexing

### Messaging & Async
- **RabbitMQ** - Event broker
- **Celery** - Background task processing

### Security
- **JWT + OAuth2** - Authentication
- **RBAC** - Role-based access control

### Observability
- **OpenTelemetry** - Distributed tracing
- **Jaeger** - Trace visualization
- **Prometheus** - Metrics collection
- **Grafana** - Metrics visualization

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Local development orchestration
- **Kubernetes** - Production deployment
- **GitHub Actions** - CI/CD Pipeline

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Make (optional, for convenience commands)

### Setup & Run

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FastApi-Issue-tracker
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start all services**
   ```bash
   make up
   # or: docker-compose up -d
   ```

4. **Verify services**
   ```bash
   # Check if all services are healthy
   curl http://localhost:8000/health
   ```

5. **View logs**
   ```bash
   make logs
   # or: docker-compose logs -f
   ```

### Development

**Install dependencies**
```bash
make install-deps
```

**Run linting and formatting**
```bash
make lint
make format
```

**Run tests**
```bash
make test
```

**Stop services**
```bash
make down
```

## 📁 Project Structure

```
FastApi-Issue-tracker/
├── services/
│   ├── api-gateway/              # API Gateway (Traefik)
│   ├── auth-service/             # Authentication service
│   ├── user-service/             # User profiles & teams
│   ├── project-service/          # Project management
│   ├── issue-service/            # Core issue tracking
│   ├── comment-service/          # Comments & mentions
│   ├── notification-service/     # Email & notifications
│   ├── search-service/           # Full-text search
│   └── audit-service/            # Activity logs & compliance
│
├── shared/
│   ├── core/                     # Core utilities
│   ├── schemas/                  # Common Pydantic models
│   ├── events/                   # Event definitions
│   └── utils/                    # Shared utilities
│
├── docker/                       # Docker configurations
├── k8s/                          # Kubernetes manifests
├── tests/                        # Integration tests
├── scripts/                      # Setup & migration scripts
├── docs/                         # Architecture documentation
│
├── Makefile                      # Development commands
├── docker-compose.yml            # Local development stack
├── .env.example                  # Environment variables template
└── README.md                     # This file
```

## 🏃 API Gateway Routes

The API Gateway routes requests to appropriate services:

```
POST   /api/v1/auth/register          → Auth Service
POST   /api/v1/auth/login             → Auth Service
GET    /api/v1/users/{id}             → User Service
POST   /api/v1/projects               → Project Service
GET    /api/v1/projects/{id}/issues   → Issue Service
POST   /api/v1/issues/{id}/comments   → Comment Service
GET    /api/v1/search                 → Search Service
```

## 🔐 Security Features

- JWT-based stateless authentication
- OAuth2 integration for third-party auth
- Role-based access control (RBAC)
- API rate limiting per service
- Distributed session management with Redis
- Audit logging of sensitive operations
- Request/response validation with Pydantic

## 📈 Scalability & Reliability

- Horizontal scaling via Kubernetes
- Service discovery with Kubernetes DNS
- Load balancing with round-robin
- Circuit breakers and retry policies
- Graceful degradation on service failures
- Health checks on all services
- Distributed tracing for debugging

## 🔄 Event-Driven Workflows

Services communicate asynchronously via RabbitMQ for:
- Issue state changes → Notification Service
- Comments posted → Audit Service
- Search index updates
- Webhook triggers
- Real-time notifications

## 📊 Observability

**Distributed Tracing**
- Every request traced end-to-end
- Context propagation between services
- Jaeger UI: http://localhost:16686

**Metrics**
- Request latency, error rates
- Database query performance
- Queue depth monitoring
- Cache hit/miss ratios

**Logging**
- Structured JSON logs
- Trace ID correlation
- Centralized log aggregation (optional)

## 🧪 Testing

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Coverage report
pytest --cov=services tests/
```

## 🚢 Deployment

### Local Development
```bash
docker-compose up
```

### Kubernetes
```bash
# Build images
docker build -t issue-tracker/<service>:latest services/<service>/

# Deploy
kubectl apply -f k8s/
```

### CI/CD
GitHub Actions automatically:
- Runs tests and linting
- Builds Docker images
- Scans for vulnerabilities
- Deploys to staging/production

## 📚 Documentation

- [Architecture Overview](docs/distributed_issue_tracker.md)
- Entity/Service Specifications:
  - [Auth Service](docs/auth_service.json)
  - [User Service](docs/user_service.json)
  - [Project Service](docs/project_service.json)
  - [Issue Service](docs/core_issue_service.json)
  - [Comment Service](docs/comment_service.json)
  - [Notification Service](docs/notification_service.json)
  - [Search Service](docs/search_service.json)
  - [Audit Service](docs/audit_service.json)

## 🔧 Development Best Practices

- Database migrations versioned with Alembic
- Schema validation with Pydantic
- Comprehensive error handling
- Request/response logging
- Type hints throughout
- Docstrings on all classes/functions

## 🤝 Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Run `make lint` and `make format`
4. Run `make test` to ensure tests pass
5. Submit a pull request

## 📋 Common Tasks

**Add a new endpoint to a service**
```
1. Create router file: services/<service>/src/routers/new_router.py
2. Add route handler with authentication
3. Add integration test in tests/
4. Update API Gateway routes if needed
```

**Add an event type**
```
1. Define schema in shared/events/schemas.py
2. Publish from source service
3. Subscribe in consumer service
4. Add integration test
```

**Debug service interaction**
```
1. Check Jaeger UI: http://localhost:16686
2. View service logs: docker-compose logs <service>
3. Verify RabbitMQ messages: http://localhost:15672
4. Check Redis: redis-cli
```

## 📞 Support

For issues or questions:
1. Check the documentation in `docs/`
2. Review service specifications
3. Check application logs
4. File an issue on GitHub

## 📄 License

MIT License - See LICENSE file for details

## 🎯 Key Learning Outcomes

This project teaches:
- Microservices design patterns
- Event-driven architecture
- Distributed system challenges
- Production observability
- Container orchestration
- API gateway patterns
- Async Python programming
- Data consistency patterns

---

**Built with ❤️ for production-grade backend engineering**
