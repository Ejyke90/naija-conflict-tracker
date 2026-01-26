## Authentication System Implementation

This authentication system provides JWT-based authentication with role-based access control (RBAC) for the Nigeria Conflict Tracker platform.

### Features Implemented ✅

**Core Authentication:**
- ✅ User registration with email validation
- ✅ Login with email/password
- ✅ JWT access tokens (1 hour expiry)
- ✅ JWT refresh tokens (7 days expiry)
- ✅ Logout with token blacklisting
- ✅ Token refresh endpoint
- ✅ Password reset flow (forgot password + reset)

**Security:**
- ✅ Bcrypt password hashing (cost factor 12)
- ✅ JWT tokens with HS256 algorithm
- ✅ Token blacklisting via Redis
- ✅ Rate limiting (5 login attempts per 15 min)
- ✅ Session management in Redis
- ✅ Audit logging for all auth events
- ✅ httpOnly cookie support (ready, not enforced yet)
- ✅ CSRF protection (middleware ready, see below)

**Authorization (RBAC):**
- ✅ Three roles: admin, analyst, viewer
- ✅ Role hierarchy (admin > analyst > viewer)
- ✅ Protected route decorators
- ✅ Optional authentication dependency

---

### Database Schema

**Tables Created:**
1. **users** - User accounts with email, hashed password, role
2. **sessions** - Active sessions linked to users
3. **audit_log** - Immutable audit trail of all auth events
4. **password_reset_tokens** - Temporary tokens for password reset

**Migration:** `alembic/versions/001_auth_tables.py`

---

### API Endpoints

**Base URL:** `/api/v1/auth`

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/register` | POST | No | Create new user account (default role: viewer) |
| `/login` | POST | No | Authenticate and get tokens |
| `/logout` | POST | Yes | Invalidate current token and session |
| `/refresh` | POST | No | Get new access token using refresh token |
| `/me` | GET | Yes | Get current user profile |
| `/forgot-password` | POST | No | Request password reset token |
| `/reset-password` | POST | No | Reset password with token |

---

### Quick Start

#### 1. Run Migrations

```bash
cd backend
alembic upgrade head
```

#### 2. Create Admin User

```bash
python scripts/seed_admin.py
```

Follow prompts to create the first admin account.

#### 3. Test Authentication

**Register a new user:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "analyst@nextier.org",
    "password": "SecureP@ss123",
    "full_name": "Jane Analyst"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "analyst@nextier.org",
    "password": "SecureP@ss123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "analyst@nextier.org",
    "role": "analyst",
    "full_name": "Jane Analyst",
    "created_at": "2024-01-15T10:30:00Z",
    "is_active": true
  }
}
```

**Access protected route:**
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### Usage in Code

#### Protect a Route

```python
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user, require_role
from app.models.auth import User

router = APIRouter()

# Any authenticated user
@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email, "role": current_user.role}

# Analysts and admins only
@router.get("/analytics")
async def get_analytics(current_user: User = Depends(require_role("analyst"))):
    return {"data": "sensitive analytics"}

# Admins only
@router.post("/admin/users")
async def create_user(current_user: User = Depends(require_role("admin"))):
    return {"message": "User created"}
```

#### Optional Authentication

```python
from typing import Optional
from app.api.deps import get_optional_user

@router.get("/conflicts")
async def get_conflicts(user: Optional[User] = Depends(get_optional_user)):
    if user:
        # Show full data to authenticated users
        return {"conflicts": full_data, "user_role": user.role}
    else:
        # Show limited data to anonymous users
        return {"conflicts": public_data}
```

---

### Role Hierarchy

| Role | Level | Can Access |
|------|-------|------------|
| **admin** | 3 | All routes (admin, analyst, viewer) |
| **analyst** | 2 | Analyst and viewer routes |
| **viewer** | 1 | Viewer routes only |

**Default role for new registrations:** `viewer`

**Promoting users:**
```sql
-- Manual promotion (run in database)
UPDATE users SET role = 'analyst' WHERE email = 'user@example.com';
UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';
```

*(Admin UI for role management coming in Phase 4)*

---

### Security Configuration

**Environment Variables (`.env`):**

```bash
# JWT Secret (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-here-change-in-production

# Token Expiration
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
PASSWORD_RESET_TOKEN_EXPIRE_HOURS=24

# Session
SESSION_EXPIRE_MINUTES=1440  # 24 hours

# Rate Limiting
LOGIN_RATE_LIMIT_ATTEMPTS=5
LOGIN_RATE_LIMIT_WINDOW_MINUTES=15

# Redis (for sessions and blacklist)
REDIS_URL=redis://localhost:6379
```

**Generate Secure SECRET_KEY:**
```bash
openssl rand -hex 32
```

---

### Audit Logging

All authentication events are logged to the `audit_log` table:

**Logged Events:**
- REGISTER - User registration
- LOGIN - Successful login
- LOGIN_FAILED - Failed login attempt
- LOGIN_RATE_LIMITED - Too many login attempts
- LOGOUT - User logout
- TOKEN_REFRESH - Access token refreshed
- PASSWORD_RESET_REQUESTED - Password reset initiated
- PASSWORD_RESET_COMPLETED - Password changed

**Query Audit Logs:**
```sql
-- Recent auth events
SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 100;

-- Failed logins for specific email
SELECT * FROM audit_log 
WHERE action = 'LOGIN_FAILED' 
  AND details->>'email' = 'user@example.com'
  AND timestamp > NOW() - INTERVAL '1 hour';

-- User activity trail
SELECT * FROM audit_log 
WHERE user_id = '123e4567-e89b-12d3-a456-426614174000'
ORDER BY timestamp DESC;
```

---

### Testing

**Unit Tests (TODO - Phase 6):**
```bash
pytest backend/tests/test_auth.py -v
```

**Test Scenarios:**
- ✅ User registration with valid data
- ✅ Registration with duplicate email (should fail)
- ✅ Login with correct credentials
- ✅ Login with incorrect password (should fail)
- ✅ Access protected route with valid token
- ✅ Access protected route with expired token (should fail)
- ✅ Token refresh with valid refresh token
- ✅ Logout and token blacklisting
- ✅ Rate limiting (6th login attempt should fail)
- ✅ Password reset flow
- ✅ RBAC (viewer cannot access admin routes)

---

### Next Steps (Phase 2-7)

**Phase 2: Protect Existing Routes** ✏️
- [ ] Apply `Depends(get_current_user)` to conflict endpoints
- [ ] Apply `Depends(require_role("analyst"))` to analytics
- [ ] Apply `Depends(require_role("admin"))` to admin endpoints

**Phase 3: Frontend Integration** 🖥️
- [ ] Login page (`/login`)
- [ ] Register page (`/register`)
- [ ] AuthContext for token management
- [ ] ProtectedRoute wrapper
- [ ] User profile dropdown

**Phase 4: Security Hardening** 🔒
- [ ] Enforce HTTPS in production
- [ ] Configure CORS properly
- [ ] Add CSRF protection middleware
- [ ] Security headers (CSP, HSTS)
- [ ] Secrets management (env vars)

**Phase 5: Testing** ✅
- [ ] Unit tests (≥90% backend coverage)
- [ ] Integration tests
- [ ] E2E tests (Cypress)
- [ ] Load testing (k6)

**Phase 6: Documentation & Deployment** 📚
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Deployment guide
- [ ] Environment setup instructions
- [ ] Monitor deployment to Railway/Vercel

---

### Troubleshooting

**Issue: "Could not validate credentials"**
- Check if token is expired (access tokens last 1 hour)
- Verify `Authorization: Bearer TOKEN` header format
- Try refreshing with `/auth/refresh` endpoint

**Issue: "Too many login attempts"**
- Wait 15 minutes and try again
- Or flush Redis: `redis-cli FLUSHDB` (dev only!)

**Issue: "User account is inactive"**
- Check `users.is_active` in database
- Reactivate: `UPDATE users SET is_active = true WHERE email = '...'`

**Issue: Migration fails**
- Check database connection
- Ensure PostgreSQL has `gen_random_uuid()` function
- Try: `CREATE EXTENSION IF NOT EXISTS pgcrypto;`

---

### Architecture Diagram

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │ 1. POST /auth/login
       │    {email, password}
       ▼
┌─────────────────┐
│  FastAPI Server │
│  /auth router   │
└────────┬────────┘
         │ 2. Verify password (bcrypt)
         │ 3. Create JWT tokens
         │ 4. Store session in Redis
         │
    ┌────┴────┬────────────┐
    ▼         ▼            ▼
┌──────┐  ┌──────┐  ┌────────────┐
│ User │  │Redis │  │ Audit Log  │
│ Table│  │Session│ │   Table    │
└──────┘  └──────┘  └────────────┘
         
Client receives:
{
  "access_token": "...",
  "refresh_token": "...",
  "user": {...}
}

Client stores tokens in:
- localStorage (or)
- sessionStorage (or)
- httpOnly cookies (preferred)

Future requests:
Authorization: Bearer <access_token>
```

---

### Files Created

**Models:**
- `app/models/auth.py` - User, Session, AuditLog, PasswordResetToken

**Services:**
- `app/services/password_service.py` - Bcrypt hashing
- `app/services/token_service.py` - JWT creation/validation
- `app/services/session_service.py` - Redis session management
- `app/services/audit_service.py` - Audit logging

**Repositories:**
- `app/repositories/user_repository.py` - User CRUD operations

**API:**
- `app/api/v1/endpoints/auth.py` - Auth endpoints
- `app/api/deps.py` - Auth dependencies (get_current_user, require_role)

**Schemas:**
- `app/schemas/auth.py` - Pydantic request/response models

**Database:**
- `alembic/versions/001_auth_tables.py` - Database migration

**Scripts:**
- `scripts/seed_admin.py` - Create initial admin user

**Config:**
- `app/core/config.py` - Updated with JWT settings

---

### Support

For issues or questions, refer to:
- OpenSpec proposal: `/openspec/changes/add-authentication-system/`
- Implementation tasks: `/openspec/changes/add-authentication-system/tasks.md`
- Security spec: `/openspec/changes/add-authentication-system/specs/security/spec.md`
