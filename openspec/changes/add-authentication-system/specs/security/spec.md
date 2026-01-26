# Delta for Security

## ADDED Requirements

### Requirement: Password Security
The system SHALL enforce secure password storage and validation practices.

#### Scenario: Password hashing on registration
- GIVEN a user creates an account with password "MyP@ssw0rd"
- WHEN the password is stored
- THEN it is hashed using bcrypt with cost factor ≥12
- AND the plaintext password is never stored
- AND the hashed password is stored in the users.hashed_password column

#### Scenario: Password validation on login
- GIVEN a user logs in with password "MyP@ssw0rd"
- WHEN authentication occurs
- THEN the plaintext password is compared against the bcrypt hash
- AND the comparison uses constant-time algorithm (prevent timing attacks)
- AND the plaintext password is discarded after validation

### Requirement: JWT Security
The system SHALL implement secure JWT token generation and validation.

#### Scenario: JWT token generation
- GIVEN a user logs in successfully
- WHEN JWT tokens are created
- THEN the access token includes:
  - Header: {"alg": "HS256", "typ": "JWT"}
  - Payload: {"user_id": "uuid", "role": "admin", "exp": timestamp, "iat": timestamp, "jti": "unique_id"}
  - Signature: HMACSHA256(header.payload, JWT_SECRET)
- AND the JWT_SECRET is at least 256 bits (32 bytes)
- AND no sensitive data (password, email) is included in payload
- AND the token expires after 1 hour

#### Scenario: JWT token validation
- GIVEN an incoming request with JWT token
- WHEN the token is validated
- THEN the signature is verified using the same JWT_SECRET
- AND the expiry (exp) claim is checked (must be future timestamp)
- AND the issued_at (iat) claim is verified (not too far in past)
- AND if any check fails, return 401 Unauthorized

### Requirement: Secure Cookie Configuration
The system SHALL use httpOnly cookies for token storage to prevent XSS attacks.

#### Scenario: Setting authentication cookies
- GIVEN a user logs in
- WHEN JWT tokens are returned
- THEN they are set as httpOnly cookies:
  - Set-Cookie: access_token=<jwt>; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=3600
  - Set-Cookie: refresh_token=<jwt>; HttpOnly; Secure; SameSite=Strict; Path=/api/v1/auth/refresh; Max-Age=604800
- AND HttpOnly prevents JavaScript access (XSS protection)
- AND Secure ensures HTTPS-only transmission
- AND SameSite=Strict prevents CSRF attacks

### Requirement: CSRF Protection
The system SHALL protect against Cross-Site Request Forgery attacks on state-changing operations.

#### Scenario: CSRF token generation
- GIVEN a user loads a page with a form
- WHEN the page renders
- THEN a CSRF token is generated and embedded in the form
- AND the token is also stored in the user's session (Redis)

#### Scenario: CSRF token validation
- GIVEN a user submits a POST request (login, register, logout)
- WHEN the request is processed
- THEN the backend validates the CSRF token matches the session
- AND if tokens don't match, return 403 Forbidden with error "CSRF validation failed"
- AND the request is blocked

### Requirement: Input Validation
The system SHALL validate all user inputs to prevent injection attacks.

#### Scenario: Email validation
- GIVEN a user submits an email during registration
- WHEN the input is validated
- THEN the email format is checked using regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- AND email length is ≤255 characters
- AND no SQL injection characters are present (validated by Pydantic)

#### Scenario: Password validation
- GIVEN a user submits a password
- WHEN the input is validated
- THEN the password length is ≥8 characters
- AND contains at least 1 uppercase letter
- AND contains at least 1 number
- AND length is ≤128 characters (prevent DoS via bcrypt)
- AND special characters are allowed but not required

### Requirement: SQL Injection Prevention
The system SHALL use parameterized queries for all database operations.

#### Scenario: Safe database query
- GIVEN a user searches for conflicts by location
- WHEN the search is executed
- THEN the query uses SQLAlchemy ORM or parameterized raw SQL
- AND user input is never concatenated into SQL strings
- AND example: `SELECT * FROM conflicts WHERE location = %s` with parameter binding

### Requirement: Rate Limiting
The system SHALL implement rate limiting to prevent abuse and DoS attacks.

#### Scenario: Login rate limiting
- GIVEN a client attempts to login
- WHEN the request is received
- THEN the backend tracks requests per IP in Redis: "ratelimit:login:{ip}"
- AND allows maximum 5 requests per 15 minutes
- AND returns 429 Too Many Requests if exceeded

#### Scenario: API rate limiting (global)
- GIVEN any authenticated user making API requests
- WHEN requests are counted
- THEN the backend allows maximum 100 requests per minute per user
- AND returns 429 Too Many Requests if exceeded
- AND includes Retry-After header with seconds to wait

### Requirement: HTTPS Enforcement
The system SHALL enforce HTTPS for all connections in production.

#### Scenario: HTTP redirect to HTTPS
- GIVEN a user accesses http://conflicts.nextier.org
- WHEN the request reaches the server
- THEN the server responds with 301 Permanent Redirect to https://conflicts.nextier.org
- AND all subsequent requests use HTTPS

#### Scenario: HSTS header
- GIVEN a user accesses the site via HTTPS
- WHEN the response is sent
- THEN the Strict-Transport-Security header is included:
  - Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
- AND the browser enforces HTTPS for 1 year

### Requirement: Security Headers
The system SHALL include security headers to protect against common web vulnerabilities.

#### Scenario: Security headers on all responses
- GIVEN any HTTP response
- WHEN headers are set
- THEN the following headers are included:
  - Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://api.mapbox.com; style-src 'self' 'unsafe-inline'
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Referrer-Policy: strict-origin-when-cross-origin

### Requirement: Secrets Management
The system SHALL securely manage sensitive configuration values.

#### Scenario: Environment variable storage
- GIVEN the application requires JWT_SECRET, DATABASE_URL, REDIS_URL
- WHEN the application starts
- THEN secrets are loaded from environment variables (not hardcoded)
- AND secrets are stored in Railway Secrets / Vercel Environment Variables
- AND secrets are never committed to git (.env files in .gitignore)

#### Scenario: Secret rotation
- GIVEN the JWT_SECRET needs to be rotated
- WHEN a new secret is deployed
- THEN existing valid tokens remain valid until expiry (grace period)
- AND new tokens are signed with the new secret
- AND old secret is removed after all tokens expire

### Requirement: Audit Trail
The system SHALL maintain immutable audit logs for security events.

#### Scenario: Immutable audit logs
- GIVEN an audit_log record is created
- WHEN the record is written to the database
- THEN it has no UPDATE or DELETE permissions (INSERT-only table)
- AND any modifications require database admin access
- AND logs are retained for at least 1 year (compliance)

#### Scenario: Audit log query for security investigation
- GIVEN a security incident occurs
- WHEN an admin investigates
- THEN they can query audit_log by user_id, action, IP address, timestamp
- AND retrieve all login attempts, data modifications, permission changes

## MODIFIED Requirements

None. No existing security system to modify.

## REMOVED Requirements

None. No insecure practices to remove (currently no auth system exists).
