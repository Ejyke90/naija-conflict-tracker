# Delta for Authentication

## ADDED Requirements

### Requirement: User Registration
The system SHALL allow users to create accounts with email and password credentials.

#### Scenario: Successful registration
- GIVEN a user visits the registration page
- WHEN the user submits a valid email and password (≥8 characters, 1 uppercase, 1 number)
- THEN a user account is created in the database
- AND the password is hashed using bcrypt with cost factor ≥12
- AND the user is assigned the default role "viewer"
- AND a success message is displayed
- AND the user is redirected to the login page

#### Scenario: Duplicate email registration
- GIVEN a user attempts to register
- WHEN the email already exists in the database
- THEN registration fails
- AND an error message "Email already registered" is displayed
- AND no database record is created

#### Scenario: Weak password rejection
- GIVEN a user attempts to register
- WHEN the password is less than 8 characters OR missing uppercase OR missing number
- THEN registration fails
- AND an error message lists password requirements
- AND no database record is created

### Requirement: User Login
The system SHALL authenticate users via email and password, issuing JWT tokens upon successful authentication.

#### Scenario: Successful login
- GIVEN a registered user with correct credentials
- WHEN the user submits email and password via POST /api/v1/auth/login
- THEN the backend verifies the bcrypt password hash
- AND generates a JWT access token (1 hour expiry)
- AND generates a JWT refresh token (7 days expiry)
- AND stores the session in Redis with user_id → token mapping
- AND returns tokens as httpOnly cookies
- AND returns user info (id, email, role, full_name) in response body
- AND updates the user's last_login timestamp
- AND logs the successful login to audit_log

#### Scenario: Failed login with invalid credentials
- GIVEN a user enters incorrect email or password
- WHEN the user submits login credentials
- THEN authentication fails
- AND an error message "Invalid email or password" is displayed
- AND no tokens are issued
- AND the failed attempt is logged to audit_log
- AND the IP address is tracked for rate limiting

#### Scenario: Account lockout after multiple failed attempts
- GIVEN a user has failed login 5 times in 15 minutes
- WHEN the user attempts to login again
- THEN the request is blocked
- AND an error message "Too many login attempts. Try again in 15 minutes" is displayed
- AND a 429 Too Many Requests status is returned

### Requirement: Protected API Endpoints
The system SHALL require valid JWT authentication for all API endpoints except authentication routes and health checks.

#### Scenario: Accessing protected endpoint with valid token
- GIVEN an authenticated user with a valid JWT token
- WHEN the user requests GET /api/v1/conflicts
- THEN the backend extracts the token from the Authorization header or httpOnly cookie
- AND verifies the JWT signature using the secret key
- AND checks the token is not blacklisted in Redis
- AND decodes user_id and role from the JWT payload
- AND attaches the user object to the request context
- AND allows the request to proceed
- AND returns the requested data

#### Scenario: Accessing protected endpoint without token
- GIVEN an unauthenticated user (no token provided)
- WHEN the user requests GET /api/v1/conflicts
- THEN the backend returns 401 Unauthorized
- AND an error message "Authentication required" is displayed
- AND no data is returned

#### Scenario: Accessing protected endpoint with expired token
- GIVEN a user with an expired JWT token (>1 hour old)
- WHEN the user requests a protected endpoint
- THEN the backend detects the expired token
- AND returns 401 Unauthorized with error "Token expired"
- AND the frontend triggers token refresh flow
- OR redirects to login if refresh token also expired

#### Scenario: Accessing protected endpoint with blacklisted token
- GIVEN a user has logged out (token blacklisted)
- WHEN the user attempts to reuse the old token
- THEN the backend finds the token in Redis blacklist
- AND returns 401 Unauthorized with error "Token revoked"
- AND redirects the user to login

### Requirement: Role-Based Access Control
The system SHALL enforce role-based permissions for administrative and analyst operations.

#### Scenario: Admin deleting a conflict
- GIVEN an authenticated user with role "admin"
- WHEN the user requests DELETE /api/v1/conflicts/{id}
- THEN the backend checks the user's role from JWT payload
- AND allows the deletion
- AND logs the action to audit_log

#### Scenario: Analyst attempting admin-only action
- GIVEN an authenticated user with role "analyst"
- WHEN the user requests DELETE /api/v1/conflicts/{id}
- THEN the backend checks the user's role
- AND returns 403 Forbidden with error "Admin role required"
- AND the deletion is blocked
- AND the attempt is logged to audit_log

#### Scenario: Viewer attempting write operation
- GIVEN an authenticated user with role "viewer"
- WHEN the user requests POST /api/v1/conflicts
- THEN the backend checks the user's role
- AND returns 403 Forbidden with error "Insufficient permissions"
- AND the creation is blocked

### Requirement: Token Refresh
The system SHALL support automatic token refresh to maintain user sessions without re-login.

#### Scenario: Refreshing an expired access token
- GIVEN a user with an expired access token but valid refresh token
- WHEN the user requests POST /api/v1/auth/refresh with the refresh token
- THEN the backend validates the refresh token signature
- AND checks the refresh token is not blacklisted
- AND generates a new access token (1 hour expiry)
- AND returns the new access token as httpOnly cookie
- AND keeps the same refresh token (unless near expiry)

#### Scenario: Automatic token refresh in frontend
- GIVEN a user making API requests
- WHEN the access token expires during usage
- THEN the frontend detects the 401 response
- AND automatically calls POST /api/v1/auth/refresh
- AND retries the original request with the new token
- AND the user experiences no interruption

### Requirement: User Logout
The system SHALL allow users to logout and invalidate their JWT tokens.

#### Scenario: Successful logout
- GIVEN an authenticated user
- WHEN the user clicks the logout button
- THEN the frontend calls POST /api/v1/auth/logout
- AND the backend extracts the JWT token
- AND adds the token's JTI (JWT ID) to Redis blacklist with TTL = token expiry
- AND clears the httpOnly cookies
- AND the frontend clears the AuthContext
- AND redirects the user to the login page
- AND logs the logout action to audit_log

#### Scenario: Logout from multiple devices
- GIVEN a user logged in on multiple devices
- WHEN the user logs out from one device
- THEN only that device's token is blacklisted
- AND other devices remain authenticated

### Requirement: Password Reset Flow
The system SHALL provide a secure password reset mechanism via email.

#### Scenario: Requesting password reset
- GIVEN a user who forgot their password
- WHEN the user submits their email via POST /api/v1/auth/forgot-password
- THEN the backend generates a secure reset token (random UUID)
- AND stores the token in the database with 1-hour expiry
- AND sends a password reset email with the token link
- AND returns a success message (even if email doesn't exist, to prevent enumeration)

#### Scenario: Completing password reset
- GIVEN a user with a valid reset token
- WHEN the user submits a new password via POST /api/v1/auth/reset-password
- THEN the backend validates the reset token (not expired, matches database)
- AND hashes the new password with bcrypt
- AND updates the user's password in the database
- AND invalidates the reset token
- AND logs the password reset to audit_log
- AND returns a success message

#### Scenario: Expired reset token
- GIVEN a user with an expired reset token (>1 hour old)
- WHEN the user attempts to reset password
- THEN the backend rejects the token
- AND returns an error "Reset token expired. Please request a new one"

### Requirement: Audit Logging
The system SHALL log all authentication-related events for security and compliance.

#### Scenario: Logging successful login
- GIVEN a user successfully logs in
- WHEN authentication completes
- THEN an audit_log record is created with:
  - user_id
  - action = "login"
  - resource = "auth.login"
  - ip_address (from request)
  - user_agent (from request headers)
  - timestamp = NOW()

#### Scenario: Logging failed login attempts
- GIVEN a user enters wrong credentials
- WHEN authentication fails
- THEN an audit_log record is created with:
  - user_id = NULL (attempt failed)
  - action = "failed_login"
  - resource = "auth.login"
  - details = {"email": "attempted_email@example.com"}
  - ip_address
  - timestamp

#### Scenario: Logging password reset
- GIVEN a user resets their password
- WHEN the reset completes
- THEN an audit_log record is created with:
  - user_id
  - action = "password_reset"
  - resource = "auth.reset-password"
  - ip_address
  - timestamp

### Requirement: Session Management
The system SHALL manage active user sessions with Redis for performance and token blacklisting.

#### Scenario: Creating a session on login
- GIVEN a user logs in successfully
- WHEN JWT tokens are issued
- THEN a session record is stored in Redis with:
  - Key: "session:{user_id}:{jti}"
  - Value: user metadata (email, role)
  - TTL: 1 hour (access token expiry)

#### Scenario: Validating session on each request
- GIVEN an authenticated request
- WHEN the backend validates the JWT
- THEN it checks Redis for the session key
- AND if the key exists, the session is valid
- AND if the key is missing, the token is considered invalid (logged out)

#### Scenario: Session timeout after inactivity
- GIVEN a user has been inactive for 30 minutes
- WHEN the user makes a new request
- THEN the backend checks the last_activity timestamp
- AND if > 30 minutes, returns 401 with "Session expired due to inactivity"
- AND removes the session from Redis
- AND the user is redirected to login

### Requirement: Rate Limiting
The system SHALL prevent brute-force attacks by rate limiting login attempts.

#### Scenario: Rate limiting by IP address
- GIVEN a client IP attempting to login
- WHEN the client makes a login request
- THEN the backend increments a counter in Redis: "ratelimit:login:{ip}"
- AND if counter > 5 within 15 minutes, block the request
- AND return 429 Too Many Requests

#### Scenario: Rate limit reset
- GIVEN a client has been rate limited
- WHEN 15 minutes have elapsed
- THEN the Redis counter expires (TTL)
- AND the client can attempt login again

## MODIFIED Requirements

None. This is a new capability with no existing authentication to modify.

## REMOVED Requirements

None. No existing authentication system to remove.
