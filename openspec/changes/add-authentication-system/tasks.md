# Implementation Tasks: Add Authentication System

## Phase 1: Backend Foundation

### 1.1 Database Setup
- [ ] 1.1.1 Create Alembic migration for `users` table (id, email, hashed_password, role, full_name, created_at, last_login, is_active)
- [ ] 1.1.2 Create Alembic migration for `sessions` table (id, user_id, token_jti, expires_at, created_at)
- [ ] 1.1.3 Create Alembic migration for `audit_log` table (id, user_id, action, resource, ip_address, user_agent, details, timestamp)
- [ ] 1.1.4 Add indexes: users(email), users(role), sessions(user_id), sessions(token_jti), audit_log(user_id), audit_log(timestamp)
- [ ] 1.1.5 Add CHECK constraint for valid roles: ('admin', 'analyst', 'viewer')
- [ ] 1.1.6 Run migrations on development database
- [ ] 1.1.7 Verify schema with `psql` or database client

### 1.2 User Model & Repository
- [ ] 1.2.1 Create `backend/app/models/user.py` with SQLAlchemy User model
- [ ] 1.2.2 Create `backend/app/models/session.py` with Session model
- [ ] 1.2.3 Create `backend/app/models/audit_log.py` with AuditLog model
- [ ] 1.2.4 Create `backend/app/repositories/user_repository.py` with CRUD methods
- [ ] 1.2.5 Add method: `get_user_by_email(email: str) -> User | None`
- [ ] 1.2.6 Add method: `create_user(email, hashed_password, role) -> User`
- [ ] 1.2.7 Add method: `update_last_login(user_id) -> None`
- [ ] 1.2.8 Add method: `update_password(user_id, new_hashed_password) -> None`

### 1.3 Password Hashing Service
- [ ] 1.3.1 Install `passlib[bcrypt]` dependency
- [ ] 1.3.2 Create `backend/app/services/password_service.py`
- [ ] 1.3.3 Implement `hash_password(plain_password: str) -> str` using bcrypt (cost=12)
- [ ] 1.3.4 Implement `verify_password(plain_password: str, hashed_password: str) -> bool`
- [ ] 1.3.5 Write unit tests for password hashing (10+ test cases)
- [ ] 1.3.6 Test bcrypt cost factor is ≥12
- [ ] 1.3.7 Test password verification with correct/incorrect passwords

### 1.4 JWT Token Service
- [ ] 1.4.1 Install `python-jose[cryptography]` dependency
- [ ] 1.4.2 Create `backend/app/services/token_service.py`
- [ ] 1.4.3 Generate JWT_SECRET (256-bit) and add to environment variables
- [ ] 1.4.4 Implement `create_access_token(user_id, role, expires_delta=1h) -> str`
- [ ] 1.4.5 Implement `create_refresh_token(user_id, expires_delta=7d) -> str`
- [ ] 1.4.6 Implement `decode_token(token: str) -> dict` (returns payload or raises exception)
- [ ] 1.4.7 Add JTI (JWT ID) to token payload for blacklisting
- [ ] 1.4.8 Write unit tests for token creation and validation (15+ test cases)
- [ ] 1.4.9 Test token expiry detection
- [ ] 1.4.10 Test invalid signature rejection

### 1.5 Redis Session Store
- [ ] 1.5.1 Create `backend/app/services/session_service.py`
- [ ] 1.5.2 Implement `create_session(user_id, token_jti, ttl=3600) -> None` (store in Redis)
- [ ] 1.5.3 Implement `get_session(token_jti) -> dict | None`
- [ ] 1.5.4 Implement `delete_session(token_jti) -> None` (for logout)
- [ ] 1.5.5 Implement `blacklist_token(token_jti, ttl) -> None` (add to Redis blacklist)
- [ ] 1.5.6 Implement `is_token_blacklisted(token_jti) -> bool`
- [ ] 1.5.7 Write unit tests with Redis mock (10+ test cases)

### 1.6 Audit Logging Service
- [ ] 1.6.1 Create `backend/app/services/audit_service.py`
- [ ] 1.6.2 Implement `log_auth_event(user_id, action, resource, request) -> None`
- [ ] 1.6.3 Extract IP address from request headers (X-Forwarded-For, X-Real-IP)
- [ ] 1.6.4 Extract user agent from request headers
- [ ] 1.6.5 Store structured details as JSONB (e.g., {"email": "user@example.com"})
- [ ] 1.6.6 Write unit tests for audit logging (8+ test cases)

## Phase 2: Authentication Endpoints

### 2.1 User Registration
- [ ] 2.1.1 Create `backend/app/api/v1/auth.py` router
- [ ] 2.1.2 Add Pydantic schema: `UserRegisterRequest` (email, password, full_name)
- [ ] 2.1.3 Add Pydantic schema: `UserRegisterResponse` (id, email, role, created_at)
- [ ] 2.1.4 Implement `POST /api/v1/auth/register` endpoint
- [ ] 2.1.5 Validate email format (regex)
- [ ] 2.1.6 Validate password strength (≥8 chars, 1 uppercase, 1 number)
- [ ] 2.1.7 Check email uniqueness (return 409 Conflict if duplicate)
- [ ] 2.1.8 Hash password with bcrypt
- [ ] 2.1.9 Create user with default role "viewer"
- [ ] 2.1.10 Return success response (no auto-login)
- [ ] 2.1.11 Write integration tests for registration (12+ test cases)
- [ ] 2.1.12 Test successful registration
- [ ] 2.1.13 Test duplicate email rejection
- [ ] 2.1.14 Test weak password rejection

### 2.2 User Login
- [ ] 2.2.1 Add Pydantic schema: `UserLoginRequest` (email, password)
- [ ] 2.2.2 Add Pydantic schema: `UserLoginResponse` (user: User, access_token, refresh_token)
- [ ] 2.2.3 Implement `POST /api/v1/auth/login` endpoint
- [ ] 2.2.4 Retrieve user by email
- [ ] 2.2.5 Verify password with bcrypt
- [ ] 2.2.6 Generate access token (1hr expiry)
- [ ] 2.2.7 Generate refresh token (7d expiry)
- [ ] 2.2.8 Create session in Redis
- [ ] 2.2.9 Set httpOnly cookies (access_token, refresh_token)
- [ ] 2.2.10 Update user.last_login timestamp
- [ ] 2.2.11 Log successful login to audit_log
- [ ] 2.2.12 Return user info (id, email, role, full_name)
- [ ] 2.2.13 Write integration tests for login (15+ test cases)
- [ ] 2.2.14 Test successful login
- [ ] 2.2.15 Test invalid email
- [ ] 2.2.16 Test invalid password
- [ ] 2.2.17 Test httpOnly cookie setting

### 2.3 Token Refresh
- [ ] 2.3.1 Add Pydantic schema: `TokenRefreshResponse` (access_token)
- [ ] 2.3.2 Implement `POST /api/v1/auth/refresh` endpoint
- [ ] 2.3.3 Extract refresh token from cookie
- [ ] 2.3.4 Validate refresh token signature
- [ ] 2.3.5 Check token not blacklisted
- [ ] 2.3.6 Generate new access token (1hr expiry)
- [ ] 2.3.7 Set new access token cookie
- [ ] 2.3.8 Return new access token in response body (for mobile apps)
- [ ] 2.3.9 Write integration tests for token refresh (8+ test cases)

### 2.4 User Logout
- [ ] 2.4.1 Implement `POST /api/v1/auth/logout` endpoint
- [ ] 2.4.2 Extract access token from request
- [ ] 2.4.3 Extract JTI from token payload
- [ ] 2.4.4 Blacklist token in Redis (TTL = remaining token lifetime)
- [ ] 2.4.5 Delete session from Redis
- [ ] 2.4.6 Clear httpOnly cookies (Set-Cookie with Max-Age=0)
- [ ] 2.4.7 Log logout to audit_log
- [ ] 2.4.8 Write integration tests for logout (6+ test cases)

### 2.5 Password Reset Flow
- [ ] 2.5.1 Add table: `password_reset_tokens` (id, user_id, token, expires_at, used)
- [ ] 2.5.2 Add Pydantic schema: `ForgotPasswordRequest` (email)
- [ ] 2.5.3 Add Pydantic schema: `ResetPasswordRequest` (token, new_password)
- [ ] 2.5.4 Implement `POST /api/v1/auth/forgot-password` endpoint
- [ ] 2.5.5 Generate secure reset token (UUID v4)
- [ ] 2.5.6 Store token in database with 1-hour expiry
- [ ] 2.5.7 Send password reset email (placeholder - log to console for now)
- [ ] 2.5.8 Return generic success message (prevent email enumeration)
- [ ] 2.5.9 Implement `POST /api/v1/auth/reset-password` endpoint
- [ ] 2.5.10 Validate reset token (exists, not expired, not used)
- [ ] 2.5.11 Hash new password with bcrypt
- [ ] 2.5.12 Update user password
- [ ] 2.5.13 Mark reset token as used
- [ ] 2.5.14 Log password reset to audit_log
- [ ] 2.5.15 Write integration tests for password reset (10+ test cases)

### 2.6 Get Current User
- [ ] 2.6.1 Add Pydantic schema: `UserResponse` (id, email, role, full_name, created_at, last_login)
- [ ] 2.6.2 Implement `GET /api/v1/auth/me` endpoint
- [ ] 2.6.3 Extract user from request context (set by auth middleware)
- [ ] 2.6.4 Return user info
- [ ] 2.6.5 Write integration tests (4+ test cases)

## Phase 3: Authorization Middleware

### 3.1 Authentication Middleware
- [ ] 3.1.1 Create `backend/app/middleware/auth_middleware.py`
- [ ] 3.1.2 Implement `get_current_user(request: Request) -> User` dependency
- [ ] 3.1.3 Extract token from Authorization header OR httpOnly cookie
- [ ] 3.1.4 Decode and validate JWT token
- [ ] 3.1.5 Check token not blacklisted in Redis
- [ ] 3.1.6 Retrieve user from database by user_id
- [ ] 3.1.7 Raise 401 Unauthorized if token invalid/missing
- [ ] 3.1.8 Return User object
- [ ] 3.1.9 Write unit tests for middleware (12+ test cases)

### 3.2 Role-Based Access Control
- [ ] 3.2.1 Create `backend/app/middleware/rbac_middleware.py`
- [ ] 3.2.2 Implement `require_role(allowed_roles: list[str])` decorator
- [ ] 3.2.3 Check current_user.role in allowed_roles
- [ ] 3.2.4 Raise 403 Forbidden if role not allowed
- [ ] 3.2.5 Write unit tests for RBAC (8+ test cases)
- [ ] 3.2.6 Test admin access to admin-only routes
- [ ] 3.2.7 Test analyst blocked from admin routes
- [ ] 3.2.8 Test viewer blocked from write operations

### 3.3 Apply Middleware to Routes
- [ ] 3.3.1 Add `dependencies=[Depends(get_current_user)]` to all protected routes
- [ ] 3.3.2 Protect `GET /api/v1/conflicts` (all roles)
- [ ] 3.3.3 Protect `POST /api/v1/conflicts` (admin, analyst)
- [ ] 3.3.4 Protect `PUT /api/v1/conflicts/{id}` (admin, analyst)
- [ ] 3.3.5 Protect `DELETE /api/v1/conflicts/{id}` (admin only)
- [ ] 3.3.6 Protect `GET /api/v1/forecasts` (all roles)
- [ ] 3.3.7 Protect `POST /api/v1/exports` (all roles)
- [ ] 3.3.8 Protect `/api/v1/admin/*` routes (admin only)
- [ ] 3.3.9 Exempt `/api/v1/auth/*` and `/health` from authentication
- [ ] 3.3.10 Write integration tests for protected routes (20+ test cases)

### 3.4 Rate Limiting
- [ ] 3.4.1 Install `slowapi` or implement custom rate limiter
- [ ] 3.4.2 Create `backend/app/middleware/rate_limit_middleware.py`
- [ ] 3.4.3 Implement login rate limiter (5 requests per 15 min per IP)
- [ ] 3.4.4 Store rate limit counters in Redis: `ratelimit:login:{ip}`
- [ ] 3.4.5 Return 429 Too Many Requests when exceeded
- [ ] 3.4.6 Add Retry-After header with seconds to wait
- [ ] 3.4.7 Implement global API rate limiter (100 req/min per user)
- [ ] 3.4.8 Write tests for rate limiting (8+ test cases)

## Phase 4: Frontend Components

### 4.1 Authentication Context
- [ ] 4.1.1 Create `frontend/lib/AuthContext.tsx`
- [ ] 4.1.2 Define AuthContext interface (user, login, logout, register, isAuthenticated, isLoading, hasRole)
- [ ] 4.1.3 Implement AuthProvider component
- [ ] 4.1.4 Add state management for user, loading, error
- [ ] 4.1.5 Implement login function (POST /api/v1/auth/login)
- [ ] 4.1.6 Implement logout function (POST /api/v1/auth/logout)
- [ ] 4.1.7 Implement register function (POST /api/v1/auth/register)
- [ ] 4.1.8 Implement hasRole helper (check user.role === role)
- [ ] 4.1.9 Add automatic token refresh logic (on 401 errors)
- [ ] 4.1.10 Wrap app with <AuthProvider> in `pages/_app.tsx`
- [ ] 4.1.11 Write unit tests for AuthContext (15+ test cases)

### 4.2 Login Page
- [ ] 4.2.1 Create `frontend/pages/login.tsx`
- [ ] 4.2.2 Design login form (email, password fields)
- [ ] 4.2.3 Use React Hook Form for form state
- [ ] 4.2.4 Add Zod schema validation (email format, password required)
- [ ] 4.2.5 Implement form submission (call AuthContext.login)
- [ ] 4.2.6 Show loading state during authentication
- [ ] 4.2.7 Display error messages (invalid credentials, server errors)
- [ ] 4.2.8 Redirect to dashboard on successful login
- [ ] 4.2.9 Add "Forgot Password?" link
- [ ] 4.2.10 Add "Don't have an account? Register" link
- [ ] 4.2.11 Style with Tailwind CSS + Shadcn/ui components
- [ ] 4.2.12 Write component tests (8+ test cases)

### 4.3 Registration Page
- [ ] 4.3.1 Create `frontend/pages/register.tsx`
- [ ] 4.3.2 Design registration form (email, password, confirm password, full name)
- [ ] 4.3.3 Use React Hook Form + Zod validation
- [ ] 4.3.4 Validate password strength (≥8 chars, 1 uppercase, 1 number)
- [ ] 4.3.5 Validate password confirmation matches
- [ ] 4.3.6 Implement form submission (call AuthContext.register)
- [ ] 4.3.7 Show success message and redirect to login
- [ ] 4.3.8 Display error messages (duplicate email, weak password)
- [ ] 4.3.9 Add "Already have an account? Login" link
- [ ] 4.3.10 Write component tests (10+ test cases)

### 4.4 Password Reset Flow
- [ ] 4.4.1 Create `frontend/pages/forgot-password.tsx`
- [ ] 4.4.2 Design form with email input
- [ ] 4.4.3 Implement POST /api/v1/auth/forgot-password
- [ ] 4.4.4 Show success message (check your email)
- [ ] 4.4.5 Create `frontend/pages/reset-password.tsx` with token parameter
- [ ] 4.4.6 Design form with new password + confirm password
- [ ] 4.4.7 Implement POST /api/v1/auth/reset-password
- [ ] 4.4.8 Show success and redirect to login
- [ ] 4.4.9 Handle expired token errors
- [ ] 4.4.10 Write component tests (8+ test cases)

### 4.5 Protected Route Wrapper
- [ ] 4.5.1 Create `frontend/components/ProtectedRoute.tsx`
- [ ] 4.5.2 Check AuthContext.isAuthenticated
- [ ] 4.5.3 If not authenticated, redirect to /login
- [ ] 4.5.4 Save original URL in query parameter (returnUrl)
- [ ] 4.5.5 After login, redirect back to original URL
- [ ] 4.5.6 Show loading spinner while checking auth
- [ ] 4.5.7 Wrap protected pages: Dashboard, Map, Forecasts, etc.
- [ ] 4.5.8 Write component tests (6+ test cases)

### 4.6 User Profile Dropdown
- [ ] 4.6.1 Create `frontend/components/UserProfileDropdown.tsx`
- [ ] 4.6.2 Display user avatar (initials or icon)
- [ ] 4.6.3 Show user name and role
- [ ] 4.6.4 Add dropdown menu items: Profile, Settings, Logout
- [ ] 4.6.5 Implement logout action (call AuthContext.logout)
- [ ] 4.6.6 Style with Radix UI DropdownMenu
- [ ] 4.6.7 Add to navigation bar in `frontend/components/Header.tsx`
- [ ] 4.6.8 Write component tests (5+ test cases)

### 4.7 Role-Based UI Elements
- [ ] 4.7.1 Create `useAuth` hook for easy context access
- [ ] 4.7.2 Implement conditional rendering based on role
- [ ] 4.7.3 Hide "Delete Conflict" button for non-admins
- [ ] 4.7.4 Hide "Admin Panel" link for non-admins
- [ ] 4.7.5 Show "Read Only" badge for viewers
- [ ] 4.7.6 Write component tests (6+ test cases)

## Phase 5: Security Hardening

### 5.1 HTTPS & Security Headers
- [ ] 5.1.1 Configure HTTPS on Railway (automatic SSL)
- [ ] 5.1.2 Configure HTTPS on Vercel (automatic SSL)
- [ ] 5.1.3 Add security headers middleware in FastAPI
- [ ] 5.1.4 Set Content-Security-Policy header
- [ ] 5.1.5 Set X-Content-Type-Options: nosniff
- [ ] 5.1.6 Set X-Frame-Options: DENY
- [ ] 5.1.7 Set Strict-Transport-Security (HSTS) header
- [ ] 5.1.8 Set Referrer-Policy header
- [ ] 5.1.9 Test headers with security scanner (securityheaders.com)

### 5.2 CORS Configuration
- [ ] 5.2.1 Install `fastapi-cors-middleware`
- [ ] 5.2.2 Configure CORS to allow only frontend domain (https://naija-conflict-tracker.vercel.app)
- [ ] 5.2.3 Set allowed methods: GET, POST, PUT, DELETE, OPTIONS
- [ ] 5.2.4 Set allow_credentials=True (for cookies)
- [ ] 5.2.5 Test CORS with different origins (should block unauthorized)

### 5.3 CSRF Protection
- [ ] 5.3.1 Install `fastapi-csrf-protect` or implement custom CSRF
- [ ] 5.3.2 Generate CSRF tokens for forms
- [ ] 5.3.3 Validate CSRF tokens on POST/PUT/DELETE requests
- [ ] 5.3.4 Exempt /api/v1/auth/login from CSRF (use double-submit cookie pattern)
- [ ] 5.3.5 Write tests for CSRF validation (8+ test cases)

### 5.4 Input Validation
- [ ] 5.4.1 Review all API endpoints for Pydantic schema validation
- [ ] 5.4.2 Add email validation regex to UserRegisterRequest
- [ ] 5.4.3 Add password strength validation to UserRegisterRequest
- [ ] 5.4.4 Sanitize all text inputs (remove SQL injection patterns)
- [ ] 5.4.5 Test with malicious inputs (SQL injection, XSS, path traversal)

### 5.5 Environment Variables
- [ ] 5.5.1 Move all secrets to .env file
- [ ] 5.5.2 Add .env to .gitignore
- [ ] 5.5.3 Document required env vars in README.md
- [ ] 5.5.4 Set JWT_SECRET in Railway (256-bit random string)
- [ ] 5.5.5 Set DATABASE_URL in Railway
- [ ] 5.5.6 Set REDIS_URL in Railway
- [ ] 5.5.7 Set FRONTEND_URL in Railway (for CORS)

## Phase 6: Testing

### 6.1 Backend Unit Tests
- [ ] 6.1.1 Write tests for password_service (10+ tests)
- [ ] 6.1.2 Write tests for token_service (15+ tests)
- [ ] 6.1.3 Write tests for session_service (10+ tests)
- [ ] 6.1.4 Write tests for audit_service (8+ tests)
- [ ] 6.1.5 Achieve ≥90% code coverage for auth module
- [ ] 6.1.6 Run pytest with coverage report

### 6.2 Backend Integration Tests
- [ ] 6.2.1 Write integration tests for /auth/register (12+ tests)
- [ ] 6.2.2 Write integration tests for /auth/login (15+ tests)
- [ ] 6.2.3 Write integration tests for /auth/logout (6+ tests)
- [ ] 6.2.4 Write integration tests for /auth/refresh (8+ tests)
- [ ] 6.2.5 Write integration tests for /auth/forgot-password (8+ tests)
- [ ] 6.2.6 Write integration tests for /auth/reset-password (10+ tests)
- [ ] 6.2.7 Write integration tests for protected routes (20+ tests)
- [ ] 6.2.8 Write integration tests for RBAC (10+ tests)

### 6.3 Frontend Unit Tests
- [ ] 6.3.1 Write tests for AuthContext (15+ tests)
- [ ] 6.3.2 Write tests for LoginPage (8+ tests)
- [ ] 6.3.3 Write tests for RegisterPage (10+ tests)
- [ ] 6.3.4 Write tests for ProtectedRoute (6+ tests)
- [ ] 6.3.5 Write tests for UserProfileDropdown (5+ tests)
- [ ] 6.3.6 Achieve ≥70% code coverage for auth components

### 6.4 End-to-End Tests
- [ ] 6.4.1 Install Cypress for E2E testing
- [ ] 6.4.2 Write E2E test: User registration → login → dashboard (happy path)
- [ ] 6.4.3 Write E2E test: Failed login → error message displayed
- [ ] 6.4.4 Write E2E test: Logout → redirect to login
- [ ] 6.4.5 Write E2E test: Access protected route → redirect to login
- [ ] 6.4.6 Write E2E test: Password reset flow
- [ ] 6.4.7 Write E2E test: Token refresh (simulate token expiry)
- [ ] 6.4.8 Run E2E tests in CI/CD pipeline

### 6.5 Security Testing
- [ ] 6.5.1 Test SQL injection resistance (automated scanner)
- [ ] 6.5.2 Test XSS resistance (inject scripts in forms)
- [ ] 6.5.3 Test CSRF protection (forged POST requests)
- [ ] 6.5.4 Test rate limiting (exceed login attempts)
- [ ] 6.5.5 Test JWT token manipulation (tampered signatures)
- [ ] 6.5.6 Test password brute-force protection
- [ ] 6.5.7 Run OWASP ZAP or Burp Suite scan
- [ ] 6.5.8 Document security test results

### 6.6 Performance Testing
- [ ] 6.6.1 Load test login endpoint (100 concurrent users)
- [ ] 6.6.2 Measure login response time (target: <500ms P95)
- [ ] 6.6.3 Measure token verification overhead (target: <10ms)
- [ ] 6.6.4 Load test protected endpoints (1,000 concurrent users)
- [ ] 6.6.5 Monitor Redis performance under load
- [ ] 6.6.6 Document performance test results

## Phase 7: Documentation & Deployment

### 7.1 API Documentation
- [ ] 7.1.1 Add OpenAPI schemas for all auth endpoints
- [ ] 7.1.2 Document request/response examples
- [ ] 7.1.3 Document error codes (401, 403, 409, 429)
- [ ] 7.1.4 Update Swagger UI at /api/docs
- [ ] 7.1.5 Add authentication section to API docs

### 7.2 User Documentation
- [ ] 7.2.1 Write user guide for registration
- [ ] 7.2.2 Write user guide for login/logout
- [ ] 7.2.3 Write user guide for password reset
- [ ] 7.2.4 Document user roles and permissions
- [ ] 7.2.5 Create FAQ for auth-related questions

### 7.3 Developer Documentation
- [ ] 7.3.1 Update README.md with auth setup instructions
- [ ] 7.3.2 Document environment variables (JWT_SECRET, etc.)
- [ ] 7.3.3 Write migration guide (running Alembic migrations)
- [ ] 7.3.4 Document auth middleware usage
- [ ] 7.3.5 Add architecture diagram (auth flow)

### 7.4 Admin Tools
- [ ] 7.4.1 Create admin seeding script: `scripts/seed_admin.py`
- [ ] 7.4.2 Script prompts for admin email and password
- [ ] 7.4.3 Script creates admin user in database
- [ ] 7.4.4 Document how to run seeding script
- [ ] 7.4.5 Add CLI command: `python scripts/seed_admin.py`

### 7.5 Deployment
- [ ] 7.5.1 Set environment variables in Railway (JWT_SECRET, etc.)
- [ ] 7.5.2 Run database migrations on production
- [ ] 7.5.3 Create initial admin user on production
- [ ] 7.5.4 Deploy backend to Railway
- [ ] 7.5.5 Deploy frontend to Vercel
- [ ] 7.5.6 Test authentication flow on production
- [ ] 7.5.7 Verify HTTPS and security headers
- [ ] 7.5.8 Monitor error logs for auth issues

### 7.6 Post-Deployment
- [ ] 7.6.1 Monitor login success/failure rates
- [ ] 7.6.2 Monitor API response times
- [ ] 7.6.3 Review audit logs for suspicious activity
- [ ] 7.6.4 Set up alerts for high failure rates (>10%)
- [ ] 7.6.5 Create runbook for common auth issues
- [ ] 7.6.6 Schedule JWT_SECRET rotation (every 90 days)

## Definition of Done

A task is complete when:
- [ ] Code is written and follows project conventions
- [ ] Unit tests written with ≥90% coverage (backend) or ≥70% (frontend)
- [ ] Integration tests pass
- [ ] Code reviewed by peer
- [ ] Documentation updated (inline comments + user guide)
- [ ] No linting errors (Black, ESLint)
- [ ] Deployed to staging and verified
- [ ] Security checklist verified

## Success Metrics

- [ ] All auth endpoints respond in <500ms (P95)
- [ ] JWT token verification takes <10ms
- [ ] Login success rate ≥95%
- [ ] Zero SQL injection vulnerabilities
- [ ] Zero XSS vulnerabilities
- [ ] Rate limiting prevents brute-force (tested)
- [ ] All audit events logged correctly
- [ ] Test coverage ≥90% (backend), ≥70% (frontend)
