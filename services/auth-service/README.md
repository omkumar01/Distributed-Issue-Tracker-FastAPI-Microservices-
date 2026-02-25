# Auth Service

Centralized authentication and JWT token management service for the issue tracker platform.

## Service Structure

```
src/
├── core/                    # Core authentication modules
│   ├── config.py           # Configuration settings
│   ├── jwt.py              # JWT token creation and validation
│   ├── security.py         # Password hashing and validation
│   └── __init__.py         # Package exports
├── models/                 # SQLAlchemy ORM models
│   ├── UserModel           # User database model
│   ├── RefreshTokenModel   # Refresh token tracking
│   ├── LoginAttemptModel   # Login attempt logging
│   └── OAuthProviderModel  # OAuth provider credentials
├── repositories/           # Data access layer
│   └── UserRepository      # User CRUD operations
├── services/               # Business logic layer
│   └── AuthService         # Authentication operations
├── schemas/                # Pydantic request/response models
│   ├── UserCreate          # User registration schema
│   ├── UserLogin           # User login schema
│   ├── UserResponse        # User response schema
│   ├── TokenResponse       # Token response schema
│   └── ... (other schemas)
├── routers/                # API endpoints
│   ├── auth_router.py      # Main auth router
│   ├── login.py            # Credential-based login
│   ├── refresh.py          # Token refresh endpoint
│   └── oauth.py            # OAuth provider endpoints
├── middleware/             # Middleware handlers
│   └── Exception handlers  # Application exception handling
├── observability/          # Tracing and metrics
│   └── OpenTelemetry       # Distributed tracing setup
├── database.py             # Database connection and session management
├── main.py                 # FastAPI application entrypoint
└── __init__.py             # Package exports
```

## Features

### Authentication
- **User Registration**: Create new user accounts with email and password
- **Credential-based Login**: Login with email and password
- **JWT Tokens**: Secure access and refresh tokens
- **Token Refresh**: Issue new access tokens without re-authentication
- **Token Validation**: Verify and decode JWT tokens
- **Password Hashing**: Bcrypt-based password hashing

### User Management
- **User Profile**: Get and update user information
- **Email Verification**: Mark user emails as verified
- **Password Management**: Change user passwords
- **Account Status**: Enable/disable user accounts

### Security
- **Password Strength Validation**: Enforce strong password requirements
- **Bcrypt Hashing**: Secure password hashing with configurable rounds
- **JWT Security**: Support for access and refresh tokens
- **CORS**: Configurable CORS middleware
- **Exception Handling**: Centralized error handling using shared exceptions

### Observability
- **OpenTelemetry Tracing**: Distributed tracing support
- **FastAPI Instrumentation**: Automatic request tracing
- **SQLAlchemy Instrumentation**: Database query tracing
- **Jaeger Integration**: Optional Jaeger tracing exporter

## API Endpoints

### Authentication

#### Register User
```
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Login
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Refresh Token
```
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Logout
```
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
```

### User

#### Get Current User
```
GET /api/v1/auth/me
Authorization: Bearer {access_token}

Response:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "last_login": "2024-01-15T15:45:00"
}
```

#### Change Password
```
POST /api/v1/auth/change-password
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "old_password": "OldPassword123!",
  "new_password": "NewPassword456!",
  "confirm_password": "NewPassword456!"
}
```

#### Verify Email
```
POST /api/v1/auth/verify-email
Authorization: Bearer {access_token}
```

### OAuth (Planned)

#### OAuth Authorization
```
GET /api/v1/auth/oauth/{provider}/authorize?redirect_uri={uri}
```

#### OAuth Callback
```
GET /api/v1/auth/oauth/{provider}/callback?code={code}&state={state}
```

#### List OAuth Providers
```
GET /api/v1/auth/oauth/providers
```

### Health Check

```
GET /health

Response:
{
  "status": "healthy",
  "service": "auth-service",
  "version": "1.0.0"
}
```

## Configuration

Environment variables (in `.env`):

```env
# Service
SERVICE_NAME=auth-service
SERVICE_VERSION=1.0.0
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres_password@postgres:5432/issue_tracker

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security
PASSWORD_MIN_LENGTH=8
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15

# Observability
JAEGER_ENABLED=false
JAEGER_HOST=jaeger
JAEGER_PORT=6831
```

## Database Models

### User
- `id` (UUID): Primary key
- `email` (String): Unique email address
- `username` (String): Unique username
- `password_hash` (String): Bcrypt hashed password
- `first_name` (String): User's first name
- `last_name` (String): User's last name
- `is_active` (Boolean): Account status
- `is_verified` (Boolean): Email verification status
- `created_at` (DateTime): Account creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `last_login` (DateTime): Last login timestamp

### RefreshToken
- `id` (UUID): Primary key
- `user_id` (UUID): User reference
- `token_hash` (String): Hashed refresh token
- `expires_at` (DateTime): Expiration timestamp
- `is_revoked` (Boolean): Revocation status
- `created_at` (DateTime): Creation timestamp
- `revoked_at` (DateTime): Revocation timestamp

### LoginAttempt
- `id` (UUID): Primary key
- `user_id` (UUID): User reference (nullable)
- `email` (String): Email address
- `ip_address` (String): Client IP address
- `success` (Boolean): Login result
- `created_at` (DateTime): Attempt timestamp

### OAuthProvider
- `id` (UUID): Primary key
- `user_id` (UUID): User reference
- `provider` (String): Provider name (google, github, etc.)
- `provider_user_id` (String): Provider's user ID
- `access_token` (String): Provider access token
- `refresh_token` (String): Provider refresh token
- `token_expires_at` (DateTime): Token expiration
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Update timestamp

## Shared Modules Integration

The auth service leverages shared modules:

- **shared.utils.exceptions**: Application-wide exception classes
  - `ApplicationException`: Base exception
  - `AuthenticationException`: Authentication errors
  - `ValidationException`: Input validation errors
  - `ResourceNotFoundException`: Resource not found errors
  - `AuthorizationException`: Authorization errors

## Error Handling

All errors return structured responses:

```json
{
  "error_code": "AUTH_FAILED",
  "message": "Invalid email or password",
  "details": {},
  "timestamp": "2024-01-15T10:30:00"
}
```

## Development

### Running the Service

```bash
# Install dependencies
pip install -r requirements.txt

# Run with uvicorn
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or using Docker
docker build -f Dockerfile -t auth-service .
docker run -p 8001:8000 --env-file .env auth-service
```

### Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

## Security Considerations

1. **Password Security**: Passwords are hashed using Bcrypt with 12 rounds
2. **JWT Secrets**: Change `SECRET_KEY` in production
3. **HTTPS**: Use HTTPS in production
4. **CORS**: Configure `allow_origins` appropriately in production
5. **Rate Limiting**: Implement rate limiting for login endpoints
6. **Token Expiration**: Access tokens expire in 30 minutes by default
7. **Refresh Token Storage**: Consider encrypting and storing refresh tokens securely

## Future Enhancements

- [ ] OAuth2 provider integration (Google, GitHub, etc.)
- [ ] Email verification endpoints
- [ ] Password reset flow
- [ ] Two-factor authentication (2FA)
- [ ] API key management for service-to-service communication
- [ ] User role management
- [ ] Permission system
- [ ] Session management
- [ ] Audit logging integration
