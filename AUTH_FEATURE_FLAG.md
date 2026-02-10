# Authentication Feature Flag

## 🚀 Overview

The authentication system can be easily toggled on/off using environment variables, making it perfect for demos, testing, and development.

## 📋 Feature Flags

### `ENABLE_AUTH`
- **Default**: `true`
- **Values**: `true` or `false`
- **Purpose**: Enable/disable authentication requirement

### `AUTH_BYPASS_USER_ID`
- **Default**: `1` (when auth is disabled)
- **Values**: Any valid user ID (integer)
- **Purpose**: Which user to impersonate when auth is disabled

## 🛠️ Usage

### **Quick Toggle Script**

```bash
# Disable authentication (demo mode)
python scripts/toggle_auth.py --disable

# Disable authentication with specific user
python scripts/toggle_auth.py --disable --user-id 2

# Enable authentication
python scripts/toggle_auth.py --enable

# Check current status
python scripts/toggle_auth.py --status
```

### **Manual Environment Variables**

Add to your `.env` file:

```bash
# Disable authentication (demo mode)
ENABLE_AUTH=false
AUTH_BYPASS_USER_ID=1

# Enable authentication (production)
ENABLE_AUTH=true
# AUTH_BYPASS_USER_ID not needed when auth is enabled
```

### **Railway Environment Variables**

In Railway dashboard, set:

- **Key**: `ENABLE_AUTH`
- **Value**: `false` (for demo) or `true` (for production)

Optional:
- **Key**: `AUTH_BYPASS_USER_ID`
- **Value**: `1` (or any valid user ID)

## 🎯 Demo Mode (`ENABLE_AUTH=false`)

When authentication is disabled:

### **What Happens**
- All endpoints become accessible without login
- A demo user is automatically provided
- No JWT validation required
- No 401 authentication errors

### **Demo User Properties**
```python
{
    "id": 1,                    # From AUTH_BYPASS_USER_ID or default
    "email": "demo@naija-conflict-tracker.com",
    "role": "admin",            # Full access
    "name": "Demo User"
}
```

### **Benefits for Demos**
- ✅ No login prompts during presentations
- ✅ No authentication errors to troubleshoot
- ✅ Instant access to all dashboard features
- ✅ Consistent demo experience

## 🔒 Production Mode (`ENABLE_AUTH=true`)

When authentication is enabled:

### **What Happens**
- JWT tokens are required for protected endpoints
- User validation and session management active
- Role-based access control enforced
- Login/logout functionality available

### **Security Features**
- ✅ JWT token validation
- ✅ Session management
- ✅ Role-based permissions
- ✅ Token blacklisting
- ✅ Refresh tokens

## 📊 Impact on Endpoints

### **Protected Endpoints** (require authentication when enabled)
- `/api/v1/analytics/*`
- `/api/v1/timeseries/*`
- `/api/v1/conflicts/*`
- `/api/v1/forecasts/*`

### **Behavior Changes**

| Feature | Auth Enabled | Auth Disabled |
|---------|--------------|---------------|
| **Monthly Trends** | Requires valid JWT | Works automatically |
| **Dashboard** | Login required | Instant access |
| **API Calls** | 401 if no token | 200 with demo data |
| **Error Handling** | Auth errors possible | No auth errors |

## 🚦 Quick Demo Setup

For a flawless demo experience:

```bash
# 1. Disable authentication
python scripts/toggle_auth.py --disable

# 2. (Optional) Set specific demo user
python scripts/toggle_auth.py --disable --user-id 1

# 3. Restart backend (Railway auto-deploys)

# 4. Test the dashboard
# Should load instantly without login prompts
```

## 🔍 Troubleshooting

### **Auth Still Required After Disabling?**
1. Check Railway environment variables
2. Restart the backend service
3. Verify `.env` file has `ENABLE_AUTH=false`

### **Demo User Not Found?**
1. Verify `AUTH_BYPASS_USER_ID` exists in database
2. Check user ID is valid integer
3. Use default demo user (ID=1) if unsure

### **Want to Re-enable Auth?**
```bash
python scripts/toggle_auth.py --enable
```

## 📝 Best Practices

### **For Demos**
- Disable authentication to avoid login friction
- Use a consistent demo user ID
- Test all features before presentation

### **For Development**
- Keep authentication enabled to test auth flows
- Use test users for different roles
- Verify error handling works

### **For Production**
- Always enable authentication
- Use strong JWT secrets
- Monitor authentication logs

## 🔄 Switching Between Modes

The feature flag can be toggled at runtime:

1. **Change environment variable**
2. **Restart backend service**
3. **New mode takes effect immediately**

No code changes required! 🎉
