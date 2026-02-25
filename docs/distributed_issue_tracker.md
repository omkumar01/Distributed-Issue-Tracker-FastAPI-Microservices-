# 🐞 Distributed Issue Tracker (FastAPI Microservices)

## 1. Project Overview

The Distributed Issue Tracker is a **cloud-native, microservices-based issue management platform** inspired by systems like Jira and Linear. It is designed to demonstrate **production-grade backend engineering**, focusing on scalability, observability, fault tolerance, and clean service boundaries.

The system enables teams to manage projects, track issues, collaborate through comments, receive real-time notifications, and search across large volumes of issues efficiently.

---

## 2. High-Level Architecture

### Architecture Style
- **Microservices Architecture**
- **API Gateway Pattern**
- **Event-Driven Architecture (EDA)** for async workflows
- **Database-per-Service Pattern**

### Core Principles
- Loose coupling between services
- Strong service ownership of data
- Horizontal scalability
- Failure isolation
- Observability-first design

---

## 3. Technology Stack

### Backend & APIs
- **FastAPI** – Async REST APIs
- **Uvicorn + Gunicorn** – ASGI server
- **Pydantic** – Data validation

### Data Layer
- **PostgreSQL** – Primary transactional DB (per service)
- **Redis** – Caching, rate limiting, locks
- **Elasticsearch / OpenSearch** – Full-text search

### Messaging & Async
- **RabbitMQ** – Event broker
- **Celery** – Background task processing

### Security
- **JWT + OAuth2** – Authentication
- **RBAC** – Authorization
- **API Gateway validation**

### Observability
- **OpenTelemetry** – Tracing & metrics
- **Prometheus** – Metrics storage
- **Grafana** – Visualization
- **Jaeger** – Distributed tracing

### Infrastructure
- **Docker** – Containerization
- **Kubernetes** – Orchestration
- **Helm** – Deployment templates
- **GitHub Actions** – CI/CD

---

## 4. Service Decomposition

### 4.1 API Gateway (Traefik)

**Responsibilities**
- Request routing
- TLS termination
- Rate limiting
- JWT validation at edge
- Circuit breaking

**Best Practices**
- Keep gateway logic minimal
- No business logic at gateway
- Fail fast for invalid requests

---

### 4.2 Auth Service

**Responsibilities**
- User authentication
- JWT issuance & refresh
- OAuth2 integration
- Token revocation

**Design Practices**
- Stateless JWT tokens
- Short-lived access tokens
- Centralized auth, decentralized authorization

---

### 4.3 User Service

**Responsibilities**
- User profile management
- Roles & team membership
- Preferences

**Design Practices**
- Avoid auth logic duplication
- Consume identity events
- Cache frequently accessed profiles

---

### 4.4 Project Service

**Responsibilities**
- Project lifecycle management
- Team & membership management
- Project-level permissions

**Design Practices**
- Project as aggregate root
- Enforce ownership boundaries
- Emit domain events on changes

---

### 4.5 Issue Service (Core Domain)

**Responsibilities**
- Issue CRUD
- Workflow state transitions
- Priority & severity
- Assignment
- SLA tracking

**Design Practices**
- Explicit workflow state machine
- Optimistic locking
- Idempotent updates
- Cache hot issues

---

### 4.6 Comment Service

**Responsibilities**
- Issue comments
- Mentions
- Edit history
- Real-time updates

**Design Practices**
- Append-only comment model
- Event-based mention handling
- WebSocket isolation

---

### 4.7 Notification Service

**Responsibilities**
- Email notifications
- In-app notifications
- Webhooks

**Design Practices**
- Fully async
- Retry with backoff
- Dead Letter Queues (DLQ)
- Respect user preferences

---

### 4.8 Search Service

**Responsibilities**
- Full-text issue search
- Filters & faceted queries

**Design Practices**
- Event-driven indexing
- Eventually consistent
- Separate read model

---

### 4.9 Audit Service

**Responsibilities**
- Activity logs
- Compliance history
- Immutable event storage

**Design Practices**
- Append-only storage
- No direct writes from services
- Long-term retention policies

---

## 5. Inter-Service Communication

### Synchronous (REST)
- Used for query-style operations
- Time-bound with timeouts

### Asynchronous (Events)
- Used for side effects
- Non-blocking workflows
- RabbitMQ topics per domain

**Best Practices**
- Idempotent consumers
- Versioned event schemas
- No cyclic dependencies

---

## 6. Database Design Best Practices

- Database per service
- No cross-service joins
- Use UUIDs for global identity
- Read replicas for scaling
- Proper indexing strategy

---

## 7. Caching Strategy

- Redis for hot data
- Cache-aside pattern
- TTL-based invalidation
- Avoid cache stampede

---

## 8. Observability & Monitoring

### OpenTelemetry
- Distributed tracing
- Context propagation
- Async workflow tracing

### Metrics
- Request latency
- Error rates
- Queue depth
- DB performance

**Best Practices**
- Golden signals (Latency, Traffic, Errors, Saturation)
- Trace every request
- Correlate logs with trace IDs

---

## 9. Reliability & Resilience

- Circuit breakers
- Timeouts
- Retries with backoff
- Bulkheads
- Graceful degradation

---

## 10. Security Best Practices

- Zero trust between services
- Validate JWT in every service
- Least privilege RBAC
- Secrets via Kubernetes Secrets
- Audit all sensitive actions

---

## 11. CI/CD Pipeline

- Linting & static analysis
- Unit & integration tests
- Docker image build
- Vulnerability scanning
- Automated deployment

---

## 12. Scalability Considerations

- Horizontal scaling via Kubernetes
- Stateless services
- Event-driven workloads
- Read/write separation

---

## 13. System Design Interview Talking Points

- Why microservices over monolith
- Event-driven consistency trade-offs
- Observability importance
- Failure isolation
- Scaling bottlenecks

---

## 14. Conclusion

This project demonstrates **real-world backend system design**, combining FastAPI microservices, event-driven architecture, and production-grade observability. It is designed not only to work but to be **operable, scalable, and debuggable** in real production environments.

---


