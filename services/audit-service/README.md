"""Audit Service Documentation."""

# Audit Service API

A production-grade audit logging and compliance service for tracking all system activities, managing compliance events, and monitoring data access.

## Features

- **Audit Logging**: Track all user actions with complete change history
- **Compliance Events**: Manage compliance-related events with configurable retention
- **Data Access Tracking**: Monitor who accessed what sensitive data and when
- **Security Monitoring**: Detect and track unauthorized access attempts
- **Full-text Search**: Search audit logs by multiple criteria
- **Statistics & Analytics**: Generate compliance reports and statistics
- **Event-Driven**: Consumes domain events from RabbitMQ for automatic logging

## API Endpoints

### Audit Logs

#### Create Audit Log
```
POST /api/v1
Content-Type: application/json

{
  "actor_id": "uuid",
  "action": "create|read|update|delete|login|logout|export|import|share|unshare",
  "resource_id": "uuid",
  "resource_type": "user|project|issue|comment|...",
  "old_values": { optional old data },
  "new_values": { optional new data },
  "changes": { what changed },
  "status": "success|failure|warning",
  "error_message": "error description if failed",
  "service": "service-name"
}

Response: 201 Created
{
  "id": "uuid",
  "actor_id": "uuid",
  "action": "create",
  "resource_id": "uuid",
  "resource_type": "user",
  ...
  "created_at": "2024-02-13T10:30:00Z"
}
```

#### Get Audit Log
```
GET /api/v1/logs/{log_id}

Response: 200 OK
{
  "id": "uuid",
  "actor_id": "uuid",
  "action": "create",
  ...
}
```

#### List Audit Logs
```
GET /api/v1/logs?actor_id=uuid&action=create&resource_type=issue&skip=0&limit=20

Query Parameters:
- actor_id: UUID (optional)
- action: string (optional)
- resource_type: string (optional)
- resource_id: UUID (optional)
- service: string (optional)
- status: success|failure|warning (optional)
- skip: int (default: 0)
- limit: int (default: 20, max: 100)

Response: 200 OK
{
  "total": 150,
  "items": [...],
  "skip": 0,
  "limit": 20
}
```

#### Get Resource Audit History
```
GET /api/v1/resource/{resource_id}?resource_type=issue

Response: 200 OK
{
  "resource_id": "uuid",
  "resource_type": "issue",
  "total_changes": 5,
  "audit_logs": [...],
  "change_timeline": [
    {
      "timestamp": "2024-02-13T10:30:00Z",
      "action": "create",
      "actor_id": "uuid",
      "changes": {...},
      "old_values": null,
      "new_values": {...}
    }
  ]
}
```

#### Get User Activity
```
GET /api/v1/user/{actor_id}/activity

Response: 200 OK
{
  "items": [...],
  "total": 42
}
```

#### Get Audit Statistics
```
GET /api/v1/stats?days=30

Query Parameters:
- days: int (1-365, default: 30)

Response: 200 OK
{
  "total_actions": 5000,
  "actions_by_type": {
    "create": 1500,
    "update": 2000,
    "delete": 500,
    "read": 1000
  },
  "actions_by_status": {
    "success": 4800,
    "failure": 200
  },
  "actions_by_service": {
    "issue-service": 2000,
    "user-service": 1500,
    ...
  },
  "actions_by_actor": {
    "uuid1": 450,
    "uuid2": 380,
    ...
  },
  "actions_last_24h": 150,
  "most_active_user": "uuid"
}
```

### Compliance Events

#### Create Compliance Event
```
POST /api/v1/compliance
Content-Type: application/json

{
  "event_type": "data_breach|policy_violation|permission_change|...",
  "severity": "critical|high|medium|low|info",
  "actor_id": "uuid",
  "action": "description_of_action",
  "resource_id": "uuid (optional)",
  "resource_type": "user|issue|... (optional)",
  "description": "detailed event description",
  "details": { additional context },
  "retention_days": "permanent" or "90"
}

Response: 201 Created
```

#### Get Compliance Event
```
GET /api/v1/compliance/{event_id}

Response: 200 OK
```

#### List Compliance Events
```
GET /api/v1/compliance?severity=critical&event_type=data_breach&skip=0&limit=50

Query Parameters:
- severity: string (optional)
- event_type: string (optional)
- skip: int (default: 0)
- limit: int (default: 50, max: 100)

Response: 200 OK
```

### Data Access Logs

#### Log Data Access
```
POST /api/v1/data-access
Content-Type: application/json

{
  "actor_id": "uuid",
  "resource_id": "uuid",
  "resource_type": "user|issue|...",
  "fields_accessed": ["email", "phone"] (optional),
  "access_method": "api|batch|internal|export",
  "operation": "read|update|delete|export",
  "ip_address": "192.168.1.1" (optional),
  "purpose": "GDPR request" (optional),
  "was_authorized": true (default)
}

Response: 201 Created
```

#### Get Data Access Log
```
GET /api/v1/data-access/{log_id}

Response: 200 OK
```

#### Get Unauthorized Access Attempts
```
GET /api/v1/data-access/unauthorized?days=30&limit=100

Query Parameters:
- days: int (1-365, default: 30)
- limit: int (1-500, default: 100)

Response: 200 OK
{
  "items": [...],
  "total": 12
}
```

#### Get Data Access Summary
```
GET /api/v1/data-access/summary?days=30

Response: 200 OK
{
  "total_accesses": 1000,
  "unauthorized_accesses": 5,
  "accesses_by_method": {
    "api": 800,
    "batch": 150,
    "internal": 50
  },
  "accesses_by_operation": {
    "read": 900,
    "export": 100
  },
  "accesses_by_actor": {
    "uuid1": 450,
    "uuid2": 350,
    ...
  }
}
```

## Event-Driven Logging

The Audit Service automatically logs events from other services via RabbitMQ:

### Subscribed Events

- **user.created** → Log user creation
- **user.updated** → Log user changes
- **user.deleted** → Log user deletion
- **project.created** → Log project creation
- **project.updated** → Log project changes
- **project.deleted** → Log project deletion
- **issue.created** → Log issue creation
- **issue.updated** → Log issue changes
- **issue.status_changed** → Log status transitions
- **issue.deleted** → Log issue deletion
- **comment.created** → Log comment creation
- **comment.updated** → Log comment edits
- **comment.deleted** → Log comment deletion
- **audit.event** → Log generic audit events

## Use Cases

### Generate Compliance Reports
```python
# Get audit stats for compliance report
GET /api/v1/stats?days=90

# Get all data access for audit trail
GET /api/v1/data-access/summary?days=90

# Get critical compliance events
GET /api/v1/compliance?severity=critical
```

### Track User Activities
```python
# See what user did
GET /api/v1/user/{user_id}/activity

# See details of specific resource
GET /api/v1/resource/{resource_id}?resource_type=issue
```

### Monitor Security
```python
# Find unauthorized access attempts
GET /api/v1/data-access/unauthorized?days=7

# Check critical compliance violations
GET /api/v1/compliance?severity=critical&days=7
```

### Investigate Issues
```python
# Get full history of resource changes
GET /api/v1/resource/{issue_id}?resource_type=issue

# See all actions by user
GET /api/v1/user/{user_id}/activity
```

## Database Schema

### audit_logs Table
- id (UUID, PK)
- actor_id (UUID, FK to users)
- action (VARCHAR 100)
- resource_id (UUID)
- resource_type (VARCHAR 100)
- old_values (JSONB)
- new_values (JSONB)
- changes (JSONB)
- status (VARCHAR 50)
- error_message (TEXT)
- ip_address (VARCHAR 45)
- user_agent (VARCHAR 255)
- service (VARCHAR 100)
- project_id (UUID, nullable)
- issue_id (UUID, nullable)
- created_at (TIMESTAMP, indexed)

### compliance_events Table
- id (UUID, PK)
- event_type (VARCHAR 100)
- severity (VARCHAR 50)
- actor_id (UUID)
- action (VARCHAR 100)
- resource_id (UUID, nullable)
- resource_type (VARCHAR 100, nullable)
- description (TEXT)
- details (JSONB)
- is_deleted (BOOLEAN)
- retention_days (VARCHAR 50)
- created_at (TIMESTAMP)
- expires_at (TIMESTAMP, nullable)

### data_access_logs Table
- id (UUID, PK)
- actor_id (UUID)
- resource_id (UUID)
- resource_type (VARCHAR 100)
- fields_accessed (JSONB)
- access_method (VARCHAR 50)
- operation (VARCHAR 50)
- ip_address (VARCHAR 45)
- purpose (VARCHAR 255)
- was_authorized (BOOLEAN)
- accessed_at (TIMESTAMP, indexed)

## Configuration

Environment variables:
```
DATABASE_URL=postgresql://user:pass@host:5432/db
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
REDIS_HOST=redis
REDIS_PORT=6379
LOG_LEVEL=INFO
ENVIRONMENT=production
```

## Performance Notes

- Indexes on: actor_id, action, resource_type, service, created_at
- Composite indexes for common queries
- Async database operations for scalability
- Event-driven design prevents direct coupling with other services

## Best Practices

1. **Always log sensitive operations** (changes, deletions, exports)
2. **Include context** (IP address, user agent, service name)
3. **Use appropriate severity levels** for compliance events
4. **Implement retention policies** for data access logs
5. **Monitor unauthorized accesses** regularly
6. **Generate periodic reports** for compliance

## Development

See [IMPLEMENTATION_GUIDE.md](../../../IMPLEMENTATION_GUIDE.md) for development instructions.
