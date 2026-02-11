# Rollback Plan: Crisis Intelligence Deployment
# Date: February 10, 2026
# Purpose: Rollback plan for Crisis Intelligence Dashboard deployment

## 🚨 **ROLLBACK TRIGGERS**
- Frontend build failures
- Crisis Intelligence Dashboard not loading
- API endpoint errors (500, 404, etc.)
- Dashboard functionality broken

## 🔄 **ROLLBACK PROCEDURES**

### **Option 1: Frontend Rollback (Quick)**
```bash
# 1. Revert to last working commit
git log --oneline -10  # Find last working commit
git revert <commit-hash>  # Revert the crisis intelligence changes
git push origin main

# 2. Or rollback to specific commit
git reset --hard <working-commit-hash>
git push --force-with-lease origin main
```

### **Option 2: Database Rollback**
```bash
# 1. Drop materialized views if they cause issues
psql 'postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require' -c "
DROP MATERIALIZED VIEW IF EXISTS crisis_monthly_summary;
DROP MATERIALIZED VIEW IF EXISTS crisis_state_hotspots;
DROP MATERIALIZED VIEW IF EXISTS crisis_actor_analysis;
DROP MATERIALIZED VIEW IF EXISTS crisis_type_distribution;
"

# 2. Remove the refresh function
psql 'postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require' -c "
DROP FUNCTION IF EXISTS refresh_crisis_intelligence_views();
"
```

### **Option 3: API Rollback**
```bash
# 1. Remove the crisis intelligence endpoint
rm backend/app/api/v1/endpoints/crisis_intelligence.py

# 2. Revert API router changes
git checkout HEAD~1 -- backend/app/api/v1/api.py

# 3. Restart backend
# If using Railway: push changes to trigger redeploy
git add .
git commit -m "Rollback: Remove crisis intelligence endpoint"
git push origin main
```

## 📁 **FILES MODIFIED**

### **Deleted Files (Can be restored from git):**
- `frontend/components/dashboard/KidnappingOverview.tsx`
- `frontend/components/dashboard/KidnappingSnapshot.tsx` 
- `frontend/components/dashboard/KidnappingTrends.tsx`

### **Modified Files:**
- `frontend/utils/api-utils.ts` - Removed deprecated fetchKidnappingStats
- `frontend/components/dashboard/ConflictDashboard.tsx` - Updated to use CrisisIntelligenceDashboard
- `frontend/pages/dashboard/index.tsx` - Updated imports and section
- `frontend/pages/conflict-dashboard.tsx` - Updated redirect URL
- `backend/app/api/v1/endpoints/crisis_intelligence.py` - New endpoint
- `backend/app/api/v1/api.py` - Added crisis intelligence router

### **New Files:**
- `frontend/components/dashboard/CrisisIntelligenceDashboard.tsx`
- `backend/database/migrations/012_create_crisis_intelligence_views_fixed.sql`

## 🔧 **RESTORE COMMANDS**

### **Restore Deleted Components:**
```bash
# Restore from git history
git checkout HEAD~1 -- frontend/components/dashboard/KidnappingOverview.tsx
git checkout HEAD~1 -- frontend/components/dashboard/KidnappingSnapshot.tsx
git checkout HEAD~1 -- frontend/components/dashboard/KidnappingTrends.tsx

# Revert API utils
git checkout HEAD~1 -- frontend/utils/api-utils.ts

# Revert dashboard changes
git checkout HEAD~1 -- frontend/components/dashboard/ConflictDashboard.tsx
git checkout HEAD~1 -- frontend/pages/dashboard/index.tsx
git checkout HEAD~1 -- frontend/pages/conflict-dashboard.tsx
```

### **Restore API Changes:**
```bash
# Remove crisis intelligence endpoint
rm backend/app/api/v1/endpoints/crisis_intelligence.py

# Revert API router
git checkout HEAD~1 -- backend/app/api/v1/api.py
```

## 🧪 **VERIFICATION STEPS**

### **After Rollback, Verify:**
1. **Frontend builds successfully**: `npm run build`
2. **Dashboard loads**: Navigate to `/dashboard`
3. **No 404/500 errors**: Check browser console
4. **API endpoints work**: Test `/api/v1/conflicts/stats/kidnapping`
5. **All cards render**: Validation queue, trends, maps, etc.

### **Test Critical Paths:**
```bash
# Test main dashboard
curl http://localhost:3000/dashboard

# Test API endpoints
curl http://localhost:8000/api/v1/conflicts/stats/kidnapping
curl http://localhost:8000/api/v1/conflicts/stats/dashboard

# Test authentication flow
# Login and verify dashboard loads
```

## 🆘 **EMERGENCY CONTACT**
- **Frontend Issues**: Check Vercel deployment logs
- **Backend Issues**: Check Railway deployment logs  
- **Database Issues**: Connect to Neon and check view status
- **API Issues**: Check backend logs for endpoint errors

## 📊 **ROLLBACK SUCCESS CRITERIA**
- ✅ Frontend builds without errors
- ✅ Dashboard loads completely
- ✅ All existing cards work (validation, trends, maps)
- ✅ No 500/404 errors in browser console
- ✅ API endpoints respond correctly
- ✅ Authentication flow works

## 🚀 **DEPLOYMENT VERIFICATION**
After rollback, ensure:
1. **Vercel deployment** completes successfully
2. **Railway backend** restarts without errors
3. **Database connectivity** works
4. **Redis caching** functions (if applicable)
5. **All user flows** work end-to-end

---
**Remember**: The old kidnapping endpoint `/api/v1/conflicts/stats/kidnapping` remains available for backward compatibility during rollback.
