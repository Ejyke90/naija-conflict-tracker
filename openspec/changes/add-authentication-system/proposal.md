# Proposal: Add Authentication System

## Intent

Implement a comprehensive JWT-based authentication and authorization system to secure the Nigeria Conflict Tracker platform. Currently, all API endpoints are publicly accessible without any authentication, creating a **critical security vulnerability** that blocks production deployment.

This change addresses the highest-priority production blocker (P0) by enabling:
- Secure user registration and login
- Role-based access control (admin, analyst, viewer)
- Session management with Redis
- Protected API endpoints
- Audit logging for compliance

## Problem Statement

### Current State
The platform has **zero authentication infrastructure**:
- ❌ All API endpoints (`/api/v1/*`) are publicly accessible
- ❌ No user accounts or login system
- ❌ No authorization checks (anyone can modify data)
- ❌ No session management
- ❌ No audit trails for user actions
- ❌ Security risk: Data manipulation, abuse, DDoS attacks

### Impact
**Blocking production deployment** - Cannot launch publicly without authentication:
- Security risk: Malicious actors could corrupt conflict data
- Legal risk: No accountability for data changes
- Compliance risk: Cannot meet NDPR/GDPR requirements
- User experience: No personalization, saved filters, or export history

### Business Value
1. **Security:** Prevent unauthorized data access and modification
2. **Compliance:** Meet NDPR (Nigerian Data Protection Regulation) requirements
3. **User Experience:** Enable personalized features (saved filters, export history)
4. **Audit Trail:** Track all data modifications for accountability
5. **Role Separation:** Differentiate between admin, analyst, and public viewer permissions

## Scope

### In Scope
**Backend (Python/FastAPI):**
- User registration endpoint (`POST /api/v1/auth/register`)
- Login endpoint with JWT issuance (`POST /api/v1/auth/login`)
- Logout endpoint with token blacklisting (`POST /api/v1/auth/logout`)
- Token refresh endpoint (`POST /api/v1/auth/refresh`)
- Password reset flow (forgot password, reset password)
- User model (email, hashed password, role, created_at)
- Role-based access control (RBAC) middleware
- Session management with Redis (token storage, blacklisting)
- Authentication middleware for protected routes
- Admin seeding script (create initial admin user)
- Audit logging for auth events (login, logout, failed attempts)
- Rate limiting for login attempts (5 per 15 minutes)

**Frontend (Next.js/React):**
- Login page component (`/pages/login.tsx`)
- Registration page component (`/pages/register.tsx`)
- Password reset flow UI (forgot password, reset confirmation)
- Authentication context provider (`AuthContext`)
- Protected route wrapper component (`ProtectedRoute`)
- User profile dropdown in navigation
- JWT token storage (httpOnly cookies)
- Automatic token refresh logic
- Role-based UI element hiding
- User info display (name, role, last login)

**Database:**
- New tables: `users`, `roles`, `sessions`, `audit_log`
- Alembic migration scripts
- Indexes for performance (email, role, token lookups)

**Security Features:**
- Password hashing with bcrypt (cost factor ≥12)
- JWT token generation and validation
- httpOnly cookies (prevent XSS)
- CSRF protection
- Input validation (Pydantic schemas)
- Rate limiting (prevent brute-force)
- Session timeout (30 minutes inactivity)

### Out of Scope
❌ OAuth/social login (Google, Microsoft) - future enhancement  
❌ Two-factor authentication (2FA) - future enhancement  
❌ Email verification for registration - future enhancement  
❌ Password strength requirements UI - use basic validation  
❌ "Remember Me" functionality - handle via token expiry  
❌ Account deletion/deactivation - admin-only feature for later  

### User Roles

| Role | Permissions | Use Cases |
|------|-------------|-----------|
| **Admin** | Full access: CRUD conflicts, manage users, view all data, configure system | Platform administrators, Nextier staff |
| **Analyst** | Read/write: Create reports, export data, view predictions, add conflicts | Security analysts, researchers |
| **Viewer** | Read-only: View dashboards, maps, charts (no data modification) | General public, journalists, students |

## Approach

### Authentication Flow
```
User Registration:
1. User submits email + password via POST /api/v1/auth/register
2. Backend validates email format, password strength (≥8 chars, 1 uppercase, 1 number)
3. Password hashed with bcrypt (cost factor 12)
4. User created in database with default role "viewer"
5. Return success message (no auto-login)

User Login:
1. User submits email + password via POST /api/v1/auth/login
2. Backend verifies credentials (compare bcrypt hash)
3. If valid: Generate JWT access token (1hr expiry) + refresh token (7 days)
4. Store session in Redis with user_id → token mapping
5. Return tokens as httpOnly cookies
6. Frontend stores user info in AuthContext

Protected Route Access:
1. Frontend includes JWT in Authorization header or cookie
2. Backend middleware extracts token, verifies signature
3. Check token not blacklisted (Redis lookup)
4. Decode user_id and role from JWT payload
5. Attach user object to request context
6. Route handler checks role permissions (e.g., @require_role("admin"))

Token Refresh:
1. Access token expires after 1 hour
2. Frontend detects 401 Unauthorized response
3. Calls POST /api/v1/auth/refresh with refresh token
4. Backend validates refresh token, issues new access token
5. Frontend retries original request with new token

Logout:
1. User clicks logout
2. Frontend calls POST /api/v1/auth/logout
3. Backend adds token to Redis blacklist (TTL = token expiry)
4. Delete httpOnly cookies
5. Frontend clears AuthContext, redirects to login
```

### Database Schema Changes

**New Tables:**

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'viewer',
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT valid_role CHECK (role IN ('admin', 'analyst', 'viewer'))
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Sessions table (Redis-backed, this is for audit/persistence)
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_jti VARCHAR(255) UNIQUE NOT NULL,  -- JWT ID for blacklisting
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_token_jti ON sessions(token_jti);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);

-- Audit log (track all auth events)
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,  -- 'login', 'logout', 'failed_login', 'password_reset'
    resource VARCHAR(255),  -- e.g., 'auth.login'
    ip_address INET,
    user_agent TEXT,
    details JSONB,  -- Store additional context
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp DESC);
```

### Technology Choices

**Why JWT over Session Cookies:**
- ✅ Stateless authentication (scales horizontally)
- ✅ Works with mobile apps / API consumers
- ✅ Decentralized verification (no DB lookup per request)
- ✅ Industry standard for modern APIs

**Why bcrypt over other hashers:**
- ✅ Industry standard, battle-tested
- ✅ Adaptive cost factor (future-proof)
- ✅ Built-in salt generation
- ✅ Python library: `passlib` with bcrypt backend

**Why Redis for session management:**
- ✅ Already in the stack (used for caching)
- ✅ Fast token blacklisting (O(1) lookups)
- ✅ TTL support (auto-expire blacklisted tokens)
- ✅ Distributed session store (multi-server support)

### API Endpoint Design

**Authentication Endpoints:**
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login (returns JWT)
- `POST /api/v1/auth/logout` - User logout (blacklist token)
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/reset-password` - Complete password reset
- `GET /api/v1/auth/me` - Get current user info

**Protected Endpoints (require authentication):**
All existing `/api/v1/*` endpoints except `/auth/*` and `/health`:
- `GET /api/v1/conflicts` - List conflicts (all roles)
- `POST /api/v1/conflicts` - Create conflict (admin, analyst)
- `PUT /api/v1/conflicts/{id}` - Update conflict (admin, analyst)
- `DELETE /api/v1/conflicts/{id}` - Delete conflict (admin only)
- `GET /api/v1/forecasts` - View forecasts (all roles)
- `POST /api/v1/exports` - Generate reports (all roles)
- `GET /api/v1/admin/*` - Admin-only endpoints (admin role)

### Frontend Integration

**Authentication Context:**
```typescript
interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  isAuthenticated: boolean;
  isLoading: boolean;
  hasRole: (role: string) => boolean;
}
```

**Protected Route Wrapper:**
```typescript
<ProtectedRoute>
  <DashboardPage />
</ProtectedRoute>
// Redirects to /login if not authenticated
```

**Role-Based UI:**
```typescript
{user?.role === 'admin' && (
  <Button>Delete Conflict</Button>
)}
```

## Success Criteria

### Functional Requirements
✅ Users can register with email + password  
✅ Users can login and receive JWT tokens  
✅ JWT tokens expire after 1 hour (auto-refresh works)  
✅ Users can logout (token blacklisted)  
✅ Password reset flow works (email-based)  
✅ All `/api/v1/*` endpoints require authentication (except `/auth/*`, `/health`)  
✅ Role-based access control enforced (admin, analyst, viewer)  
✅ Unauthorized access returns 401/403 with clear error messages  
✅ Audit logs capture login, logout, failed attempts  

### Security Requirements
✅ Passwords hashed with bcrypt (cost factor ≥12)  
✅ JWT tokens signed with secure secret (256-bit minimum)  
✅ httpOnly cookies prevent XSS attacks  
✅ CSRF protection enabled for state-changing operations  
✅ Rate limiting active (5 login attempts per 15 minutes)  
✅ Session timeout after 30 minutes of inactivity  
✅ No sensitive data in JWT payload (user_id and role only)  
✅ Token blacklisting prevents reuse of logged-out tokens  

### Performance Requirements
✅ Login response time: <500ms (P95)  
✅ Token verification overhead: <10ms per request  
✅ Redis session lookups: <5ms  
✅ Support 1,000 concurrent authenticated users  

### User Experience Requirements
✅ Clear error messages for failed login ("Invalid email or password")  
✅ Loading states during login/logout  
✅ Redirect to originally requested page after login  
✅ User info visible in navigation (name, role)  
✅ Graceful handling of expired tokens (auto-refresh or re-login prompt)  

## Migration Strategy

### Phase 1: Backend Foundation (Week 1)
1. Create database tables (`users`, `sessions`, `audit_log`)
2. Implement User model and authentication service
3. Build authentication endpoints (register, login, logout, refresh)
4. Add JWT generation and validation utilities
5. Implement bcrypt password hashing
6. Set up Redis session store

### Phase 2: Authorization & Middleware (Week 1-2)
1. Create authentication middleware (`@require_auth` decorator)
2. Implement role-based access control (`@require_role("admin")`)
3. Apply middleware to all protected endpoints
4. Add rate limiting for login attempts
5. Implement audit logging

### Phase 3: Frontend Integration (Week 2)
1. Build login/registration page components
2. Create AuthContext provider
3. Implement protected route wrapper
4. Add token refresh logic
5. Build user profile dropdown
6. Implement password reset UI

### Phase 4: Testing & Hardening (Week 2-3)
1. Write unit tests for auth endpoints (≥90% coverage)
2. Test role-based access control
3. Security testing (XSS, CSRF, brute-force)
4. Load testing (1,000 concurrent users)
5. Penetration testing (token manipulation, session hijacking)

### Phase 5: Deployment (Week 3)
1. Create admin seeding script for production
2. Update environment variables (JWT_SECRET, BCRYPT_ROUNDS)
3. Deploy to staging, verify all flows
4. Update API documentation (OpenAPI/Swagger)
5. Deploy to production

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| JWT secret leaked | High (all tokens compromised) | Low | Store in secrets manager, rotate regularly |
| Session hijacking | High (unauthorized access) | Medium | Use httpOnly cookies, HTTPS only, short token expiry |
| Brute-force attacks | Medium (account takeover) | High | Rate limiting (5 attempts/15min), account lockout |
| Redis downtime | High (no auth works) | Low | Failover to PostgreSQL sessions, health checks |
| Breaking existing API consumers | Medium (disruption) | Medium | Gradual rollout, deprecation warnings, docs |
| Password reset abuse | Low (spam) | Medium | Rate limit reset requests, CAPTCHA (future) |

## Timeline Estimate

- **Backend Development:** 3-4 days (auth endpoints, middleware, models)
- **Frontend Development:** 3-4 days (login UI, AuthContext, protected routes)
- **Testing:** 2-3 days (unit, integration, security tests)
- **Documentation:** 1 day (API docs, user guide)
- **Deployment:** 1 day (staging + production)

**Total:** 10-13 days (2-2.5 weeks) with 1 full-time developer

## Open Questions

1. **Email Service:** Which email provider for password resets? (SendGrid, AWS SES, Mailgun)
2. **Admin Creation:** How to create the first admin user? (CLI script, manual database insert)
3. **Session Persistence:** Should sessions survive server restarts? (Redis persistence vs in-memory)
4. **Token Expiry:** Is 1 hour too short for access tokens? Consider UX vs security tradeoff.
5. **Registration:** Should registration be open to public or admin-only user creation?
6. **Password Policy:** Enforce complexity (uppercase, numbers, special chars) or just minimum length?
7. **Multi-Device:** Should users be able to have concurrent sessions on multiple devices?
8. **Account Recovery:** Email-based only or add security questions / backup codes?

## References

- **OWASP Authentication Cheat Sheet:** https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **JWT Best Practices:** https://tools.ietf.org/html/rfc8725
- **FastAPI Security Guide:** https://fastapi.tiangolo.com/tutorial/security/
- **NDPR Compliance:** Nigerian Data Protection Regulation requirements
- **Related Task List:** See `PRODUCTION_TASKS.md` Phase 1 (AUTH-1 to AUTH-20, SEC-1 to SEC-10)
