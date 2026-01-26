# Frontend Authentication - Phase 3 Complete ✅

## Overview

The frontend now has complete JWT authentication integrated with the backend API. This includes login/register pages, protected routes, role-based access control, and user profile management.

---

## 🎯 Features Implemented

### 1. **AuthContext** (`/contexts/AuthContext.tsx`)
Global authentication state management with:
- JWT token storage in localStorage
- User state management (user, loading, error)
- Auto token refresh every 50 minutes
- Login/logout/register functions
- Role-based access helper (`hasRole()`)

### 2. **Login Page** (`/pages/login.tsx`)
- Email/password form
- Error handling with alerts
- Registration success message
- Redirect to dashboard after login
- Link to register and forgot password pages

### 3. **Register Page** (`/pages/register.tsx`)
- Full name, email, password fields
- Password confirmation validation
- Password strength requirement (8+ characters)
- Role information box (new users start as "viewer")
- Redirect to login after successful registration

### 4. **ProtectedRoute Component** (`/components/ProtectedRoute.tsx`)
HOC wrapper for pages requiring authentication:
- Redirects to login if not authenticated
- Supports role-based access control (RBAC)
- Loading spinner while checking auth
- Unauthorized redirect if insufficient role

### 5. **Unauthorized Page** (`/pages/unauthorized.tsx`)
- Shown when user doesn't have required role
- Displays role hierarchy explanation
- Back button and dashboard link

### 6. **Updated DashboardHeader** (`/components/layout/DashboardHeader.tsx`)
Enhanced header with:
- User profile dropdown (avatar, name, email, role badge)
- Logout button
- Profile link
- Dashboard link
- Sign in/register buttons for unauthenticated users

### 7. **Protected Pages**
- `/pages/analytics.tsx` - Requires "analyst" role
- `/pages/forecasts.tsx` - Requires "analyst" role
- Main dashboard (`/pages/index.tsx`) - Public (viewers can access)

---

## 🔐 Role-Based Access Control (RBAC)

**Role Hierarchy:**
```
viewer (1)   → Can view data and maps (read-only)
analyst (2)  → Can view + create/edit conflicts + run analytics/forecasts
admin (3)    → Full access + user management + delete operations
```

**Role Permissions:**
- **Public routes:** Home, Map, Login, Register
- **Viewer routes:** Dashboard, Conflict Index (read-only)
- **Analyst routes:** Analytics, Forecasts, Create/Edit Conflicts
- **Admin routes:** User Management, Delete Conflicts

---

## 🚀 Setup Instructions

### 1. Environment Variables

Create `/frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8080
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token_here
```

**Production (Vercel):**
```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token_here
```

### 2. Install Dependencies (if needed)

The authentication uses existing dependencies:
- `@tanstack/react-query` - Already installed ✅
- `next`, `react`, `react-dom` - Already installed ✅
- No additional packages needed!

### 3. Run Development Server

```bash
cd frontend
npm run dev
```

Visit http://localhost:3000

---

## 📖 Usage Examples

### Protecting a Page with ProtectedRoute

```tsx
import ProtectedRoute from '@/components/ProtectedRoute';

export default function MyPage() {
  return (
    <ProtectedRoute requiredRole="analyst">
      <YourComponent />
    </ProtectedRoute>
  );
}
```

### Using Auth in Components

```tsx
import { useAuth } from '@/contexts/AuthContext';

function MyComponent() {
  const { user, isAuthenticated, logout } = useAuth();

  if (!isAuthenticated) {
    return <p>Please login</p>;
  }

  return (
    <div>
      <p>Welcome, {user?.full_name}!</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### Making Authenticated API Calls

```tsx
import { getAccessToken } from '@/contexts/AuthContext';

async function fetchProtectedData() {
  const token = getAccessToken();
  
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/analytics/hotspots`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) throw new Error('Failed to fetch');
  return response.json();
}
```

### Checking User Role

```tsx
import { useAuth, hasRole } from '@/contexts/AuthContext';

function AdminButton() {
  const { user } = useAuth();

  // Only show button if user is admin
  if (!hasRole(user, 'admin')) {
    return null;
  }

  return <button>Admin Action</button>;
}
```

---

## 🔄 Authentication Flow

### Registration Flow
1. User fills out register form (`/pages/register.tsx`)
2. Frontend calls `authAPI.register(data)`
3. Backend creates user with "viewer" role
4. User redirected to login page with success message
5. User logs in with credentials

### Login Flow
1. User enters email/password (`/pages/login.tsx`)
2. Frontend calls `authAPI.login(credentials)`
3. Backend validates credentials, creates session
4. Backend returns JWT tokens + user data
5. Frontend stores tokens in localStorage
6. Frontend redirects to dashboard

### Protected Page Access
1. User navigates to protected page (e.g., `/analytics`)
2. `ProtectedRoute` checks `isAuthenticated` and `user.role`
3. If not authenticated → redirect to `/login`
4. If insufficient role → redirect to `/unauthorized`
5. If authorized → render page content

### Logout Flow
1. User clicks logout button
2. Frontend calls `authAPI.logout(token)`
3. Backend blacklists token in Redis
4. Frontend clears localStorage
5. Frontend redirects to `/login`

### Auto Token Refresh
1. `AuthContext` sets interval (50 minutes)
2. Calls `authAPI.refreshToken(refreshToken)`
3. Backend validates refresh token
4. Backend returns new access token
5. Frontend updates localStorage

---

## 🧪 Testing the Authentication

### Test Accounts

**Admin Account:**
```
Email: admin@nextier.org
Password: admin123
Role: admin
```

**Analyst Account:**
```
Email: analyst@example.com
Password: analyst123
Role: analyst
```

**Viewer Account:**
- Register new account at `/register`
- Default role: viewer

### Test Scenarios

1. **Register New User**
   - Go to `/register`
   - Fill form, submit
   - Should redirect to `/login` with success message

2. **Login**
   - Go to `/login`
   - Enter credentials
   - Should redirect to dashboard

3. **Protected Routes**
   - Without login, visit `/analytics`
   - Should redirect to `/login`

4. **Role Access**
   - Login as viewer
   - Try to access `/analytics`
   - Should redirect to `/unauthorized`

5. **Logout**
   - Login
   - Click user dropdown → Sign Out
   - Should redirect to `/login`

6. **Token Persistence**
   - Login
   - Refresh page
   - User should still be logged in

---

## 🛠️ API Endpoints Used

All authentication endpoints are defined in `/backend/app/api/v1/endpoints/auth.py`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Create new user |
| `/api/v1/auth/login` | POST | Login, get tokens |
| `/api/v1/auth/logout` | POST | Blacklist token |
| `/api/v1/auth/me` | GET | Get current user |
| `/api/v1/auth/refresh` | POST | Refresh access token |
| `/api/v1/auth/forgot-password` | POST | Request password reset |
| `/api/v1/auth/reset-password` | POST | Reset password |

---

## 📁 File Structure

```
frontend/
├── contexts/
│   └── AuthContext.tsx          # Global auth state
├── lib/
│   └── auth-api.ts              # API client
├── components/
│   ├── ProtectedRoute.tsx       # Route wrapper
│   └── layout/
│       └── DashboardHeader.tsx  # Header with user dropdown
├── pages/
│   ├── _app.tsx                 # App wrapper with AuthProvider
│   ├── login.tsx                # Login page
│   ├── register.tsx             # Register page
│   ├── unauthorized.tsx         # Unauthorized page
│   ├── analytics.tsx            # Protected (analyst)
│   └── forecasts.tsx            # Protected (analyst)
└── .env.example                 # Environment variables template
```

---

## 🔒 Security Features

1. **JWT Tokens:**
   - Access token: 1 hour expiry
   - Refresh token: 7 days expiry
   - Bearer authentication scheme

2. **Token Blacklisting:**
   - Logout blacklists tokens in Redis
   - Prevents token reuse after logout

3. **Auto Token Refresh:**
   - Refreshes tokens every 50 minutes
   - Prevents session expiration

4. **Password Security:**
   - Bcrypt hashing on backend
   - Minimum 8 characters required
   - Confirmation validation

5. **RBAC Hierarchy:**
   - Higher roles inherit lower role permissions
   - Viewer < Analyst < Admin

6. **HTTPS in Production:**
   - ⚠️ TODO: Enforce HTTPS (Phase 4)
   - ⚠️ TODO: httpOnly cookies instead of localStorage (Phase 4)

---

## ⏭️ Next Steps (Phase 4)

1. **Security Hardening:**
   - Move tokens to httpOnly cookies (more secure than localStorage)
   - Enforce HTTPS in production
   - Add CSRF protection
   - Configure CORS whitelist
   - Add rate limiting on frontend

2. **Password Reset:**
   - Implement forgot password page (`/pages/forgot-password.tsx`)
   - Implement reset password page (`/pages/reset-password.tsx`)

3. **User Profile:**
   - Create profile page (`/pages/profile.tsx`)
   - Allow users to update name, email
   - Change password functionality

4. **Admin Panel:**
   - User management page (list, edit roles, delete)
   - Audit log viewer
   - Session management

5. **Testing:**
   - Unit tests for AuthContext
   - Component tests for login/register
   - E2E tests with Playwright/Cypress

---

## 🐛 Troubleshooting

### "Network Error" on Login
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Ensure backend is running on port 8080
- Check browser console for CORS errors

### Infinite Redirect Loop
- Clear localStorage: `localStorage.clear()`
- Check backend health: `curl http://localhost:8080/health`

### "Token expired" Error
- Login again (tokens expire after 1 hour)
- Check auto-refresh logic in `AuthContext`

### Role Access Issues
- Check user role: `localStorage.getItem('user')`
- Verify backend RBAC in `/backend/app/api/deps.py`

---

## ✅ Phase 3 Completion Checklist

- [x] Create AuthContext with token management
- [x] Create Login page
- [x] Create Register page
- [x] Create ProtectedRoute component
- [x] Create Unauthorized page
- [x] Update DashboardHeader with user dropdown
- [x] Wrap _app.tsx with AuthProvider
- [x] Protect analytics page (analyst role)
- [x] Protect forecasts page (analyst role)
- [x] Create .env.example
- [x] Write comprehensive documentation

**Phase 3 is 100% complete!** 🎉

---

## 📚 Related Documentation

- Backend Auth: `/backend/app/api/v1/endpoints/auth.py`
- Database Models: `/backend/app/models/auth.py`
- API Docs: http://localhost:8080/docs (when backend running)
- Phase 1 Summary: See conversation history
- Phase 2 Summary: See conversation history

---

**Questions?** Check the API documentation at http://localhost:8080/docs or review the backend auth implementation.
