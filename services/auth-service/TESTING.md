# Auth Service - Testing Guide

Complete testing guide for the Auth Service including all endpoints and edge cases.

## Service Status

✅ **Auth Service Running**
- Container: `fastapi-issue-tracker-auth-service-1`
- URL: `http://localhost:8001`
- Database: Ready and initialized with tables
- Swagger Docs: `http://localhost:8001/docs`

---

## Password Validation Rules

**Valid Password Example:** `SecurePass123!`

Requirements:
- ✅ Minimum 8 characters long
- ✅ At least one uppercase letter (A-Z)
- ✅ At least one lowercase letter (a-z)
- ✅ At least one digit (0-9)
- ✅ Maximum 72 bytes when UTF-8 encoded (bcrypt limit)

**Invalid Passwords:**
- `short123` - Too short
- `nouppercase123` - No uppercase
- `NOLOWERCASE123` - No lowercase
- `NoDigits!` - No digits
- Very long password with 100+ characters - Exceeds bcrypt 72-byte limit

---

## Test Cases

### 1. Health Check

**Request:**
```
GET /health
```

**Expected Response (200):**
```json
{
  "status": "healthy",
  "service": "auth-service",
  "version": "1.0.0"
}
```

### 2. Register User - Valid Password

**Request:**
```
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "john@example.com",
  "username": "john_doe",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Expected Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2026-02-13T10:30:00",
  "updated_at": "2026-02-13T10:30:00",
  "last_login": null
}
```

### 3. Register User - Password Too Short

**Request:**
```
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "jane@example.com",
  "username": "jane_doe",
  "password": "short1!",
  "first_name": "Jane",
  "last_name": "Doe"
}
```

**Expected Response (422):**
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Password must be at least 8 characters long",
  "details": {},
  "timestamp": "2026-02-13T10:30:00"
}
```

### 4. Register User - Password Missing Uppercase

**Request:**
```
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "bob@example.com",
  "username": "bob_smith",
  "password": "nouppercase123!",
  "first_name": "Bob",
  "last_name": "Smith"
}
```

**Expected Response (422):**
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Password must contain uppercase, lowercase, and digit",
  "details": {},
  "timestamp": "2026-02-13T10:30:00"
}
```

### 5. Register User - Password Exceeds 72 Bytes

**Request:**
```
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "long@example.com",
  "username": "longpassword",
  "password": "VeryLongPassword123!WithManySpecialCharacters@#$%^&*()_+~`|{}[]:<>?,./ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnop",
  "first_name": "Long",
  "last_name": "Password"
}
```

**Expected Response (422):**
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Password must not exceed 72 bytes when encoded in UTF-8 (consider a shorter password or fewer special characters)",
  "details": {},
  "timestamp": "2026-02-13T10:30:00"
}
```

### 6. Register User - Email Already Exists

**Request (after registering john@example.com first):**
```
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "john@example.com",
  "username": "john_doe2",
  "password": "AnotherPass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Expected Response (422):**
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Email already registered",
  "details": {},
  "timestamp": "2026-02-13T10:30:00"
}
```

### 7. Register User - Username Already Exists

**Request (after registering john_doe first):**
```
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "another@example.com",
  "username": "john_doe",
  "password": "AnotherPass123!",
  "first_name": "Another",
  "last_name": "User"
}
```

**Expected Response (422):**
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Username already taken",
  "details": {},
  "timestamp": "2026-02-13T10:30:00"
}
```

### 8. Login - Valid Credentials

**Request:**
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Save the `access_token`** for subsequent requests.

### 9. Login - Invalid Password

**Request:**
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "WrongPassword123!"
}
```

**Expected Response (401):**
```json
{
  "error_code": "AUTH_FAILED",
  "message": "Invalid email or password",
  "details": {},
  "timestamp": "2026-02-13T10:30:00"
}
```

### 10. Login - Non-Existent Email

**Request:**
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "nonexistent@example.com",
  "password": "SomePassword123!"
}
```

**Expected Response (401):**
```json
{
  "error_code": "AUTH_FAILED",
  "message": "Invalid email or password",
  "details": {},
  "timestamp": "2026-02-13T10:30:00"
}
```

### 11. Get Current User

**Request:**
```
GET /api/v1/auth/me
Authorization: Bearer {access_token}
```

**Expected Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2026-02-13T10:30:00",
  "updated_at": "2026-02-13T10:30:00",
  "last_login": "2026-02-13T10:35:00"
}
```

### 12. Get Current User - Invalid Token

**Request:**
```
GET /api/v1/auth/me
Authorization: Bearer invalid_token_here
```

**Expected Response (401):**
```json
{
  "error_code": "AUTH_FAILED",
  "message": "Invalid or expired token",
  "details": {},
  "timestamp": "2026-02-13T10:30:00"
}
```

### 13. Get Current User - Missing Authorization Header

**Request:**
```
GET /api/v1/auth/me
```

**Expected Response (401):**
```json
{
  "detail": "Missing authorization header"
}
```

### 14. Refresh Token

**Request:**
```
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 15. Change Password

**Request:**
```
POST /api/v1/auth/change-password
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "old_password": "SecurePass123!",
  "new_password": "NewPassword456!",
  "confirm_password": "NewPassword456!"
}
```

**Expected Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

### 16. Change Password - Wrong Old Password

**Request:**
```
POST /api/v1/auth/change-password
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "old_password": "WrongOldPassword123!",
  "new_password": "NewPassword456!",
  "confirm_password": "NewPassword456!"
}
```

**Expected Response (401):**
```json
{
  "error_code": "AUTH_FAILED",
  "message": "Invalid current password",
  "details": {},
  "timestamp": "2026-02-13T10:30:00"
}
```

### 17. Change Password - New Passwords Don't Match

**Request:**
```
POST /api/v1/auth/change-password
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "old_password": "SecurePass123!",
  "new_password": "NewPassword456!",
  "confirm_password": "DifferentPassword789!"
}
```

**Expected Response (422):**
```json
{
  "detail": "Passwords do not match"
}
```

### 18. Verify Email

**Request:**
```
POST /api/v1/auth/verify-email
Authorization: Bearer {access_token}
```

**Expected Response (200):**
```json
{
  "message": "Email verified successfully"
}
```

### 19. Logout

**Request:**
```
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
```

**Expected Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

---

## Password Edge Cases to Test

### UTF-8 Special Characters (72-byte limit)

Example with emoji (each emoji can be 4 bytes in UTF-8):

**Test 1: Valid password with special characters**
```json
{
  "email": "special@example.com",
  "username": "specialuser",
  "password": "SecurePass123!@#$%",
  "first_name": "Special",
  "last_name": "Chars"
}
```
✅ Should succeed (35 bytes)

**Test 2: Very long special characters exceeding 72 bytes**
```json
{
  "email": "veryspecial@example.com",
  "username": "veryspecialuser",
  "password": "SecurePass123!@#$%^&*()_+~`|{}[]:;<>?,./\\"VeryLong",
  "first_name": "Very",
  "last_name": "Special"
}
```
❌ Should fail (>72 bytes)

---

## Testing Checklist

- [ ] Health check endpoint works
- [ ] User registration with valid password succeeds
- [ ] Password validation rejects short passwords (< 8 chars)
- [ ] Password validation rejects passwords without uppercase
- [ ] Password validation rejects passwords without lowercase
- [ ] Password validation rejects passwords without digits
- [ ] Password validation rejects passwords > 72 bytes (UTF-8)
- [ ] Duplicate email registration fails
- [ ] Duplicate username registration fails
- [ ] Login with correct credentials succeeds
- [ ] Login with incorrect password fails
- [ ] Login updates last_login timestamp
- [ ] Get current user returns correct user data
- [ ] Get current user fails without token
- [ ] Get current user fails with invalid token
- [ ] Token refresh generates new tokens
- [ ] Change password succeeds with correct old password
- [ ] Change password fails with incorrect old password
- [ ] Email verification marks user as verified
- [ ] Logout endpoint responds successfully

---

## Manual Testing Commands

### 1. Register User (using PowerShell)

```powershell
$body = @{
    email = "testuser@example.com"
    username = "testuser"
    password = "TestPass123!"
    first_name = "Test"
    last_name = "User"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8001/api/v1/auth/register" `
  -Method Post `
  -Headers @{"Content-Type" = "application/json"} `
  -Body $body

$response.Content | ConvertFrom-Json | ConvertTo-Json
```

### 2. Login User

```powershell
$body = @{
    email = "testuser@example.com"
    password = "TestPass123!"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8001/api/v1/auth/login" `
  -Method Post `
  -Headers @{"Content-Type" = "application/json"} `
  -Body $body

$loginResponse = $response.Content | ConvertFrom-Json
$accessToken = $loginResponse.access_token
Write-Host "Access Token: $accessToken"
```

### 3. Get Current User

```powershell
$accessToken = "YOUR_TOKEN_HERE"

$response = Invoke-WebRequest -Uri "http://localhost:8001/api/v1/auth/me" `
  -Method Get `
  -Headers @{"Authorization" = "Bearer $accessToken"} `
  -ContentType "application/json"

$response.Content | ConvertFrom-Json | ConvertTo-Json
```

### 4. Test Password Validation (Too Long)

```powershell
$longPassword = "VeryLongPassword123!WithManySpecialCharacters@#$%^&*()_+~`|{}[]:<>?,./ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnop"

$body = @{
    email = "longuser@example.com"
    username = "longuser"
    password = $longPassword
    first_name = "Long"
    last_name = "Pass"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8001/api/v1/auth/register" `
  -Method Post `
  -Headers @{"Content-Type" = "application/json"} `
  -Body $body `
  -ErrorAction SilentlyContinue

# Should return 422 error about password being too long
$response.Content | ConvertFrom-Json | ConvertTo-Json
```

---

## Fixes Applied

### 1. Bcrypt 72-Byte Limit Handling
- Added validation in `validate_password_strength()` to check UTF-8 encoded byte length
- Added defensive truncation in `hash_password()` method
- Error message clearly explains the limitation

### 2. Database Auto-Initialization
- Tables are created automatically on service startup
- No manual migrations needed for development

### 3. Docker Configuration
- All dependencies properly installed
- File paths correctly configured
- Service runs on port 8001

---

## Expected Behavior Summary

| Operation | Valid Input | Result |
|-----------|-------------|--------|
| Register | Valid password (8-72 bytes, upper/lower/digit) | ✅ User created |
| Register | Password < 8 chars | ❌ Validation error |
| Register | No uppercase letter | ❌ Validation error |
| Register | No lowercase letter | ❌ Validation error |
| Register | No digit | ❌ Validation error |
| Register | Password > 72 bytes UTF-8 | ❌ Validation error |
| Register | Email already registered | ❌ Duplicate error |
| Register | Username already taken | ❌ Duplicate error |
| Login | Correct credentials | ✅ Tokens issued |
| Login | Wrong password | ❌ Auth failed |
| Login | Non-existent email | ❌ Auth failed |
| Get User | Valid token | ✅ User data returned |
| Get User | Invalid token | ❌ Auth failed |
| Get User | No token | ❌ Missing header |
| Refresh | Valid refresh token | ✅ New tokens issued |
| Refresh | Invalid/expired token | ❌ Auth failed |

---

**Last Updated:** February 13, 2026  
**Service:** Auth Service v1.0.0  
**Status:** ✅ Ready for Testing
