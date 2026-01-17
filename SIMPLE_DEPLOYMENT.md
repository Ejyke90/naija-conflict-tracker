# 🚀 Simple Deployment Guide (No GitHub Actions Required)

## Why This Approach is Better

GitHub Actions requires setting up multiple secrets and tokens which can be complex. Direct deployment through the platforms is:
- ✅ Faster and simpler
- ✅ No secret management needed
- ✅ Better error handling
- ✅ Full control over deployment

## 📋 Step-by-Step Deployment

### 1. Deploy Backend to Railway (5 minutes)

1. **Go to Railway**: https://railway.app
2. **Click "New Project"**
3. **Click "Deploy from GitHub repo"**
4. **Select your repository**: `naija-conflict-tracker`
5. **Configure Service**:
   - Root Directory: `./backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. **Add Database**:
   - Click "New Service" → PostgreSQL
   - Add extensions: `postgis`, `timescaledb`
7. **Deploy**: Click the Deploy button!

### 2. Deploy Frontend to Vercel (3 minutes)

1. **Go to Vercel**: https://vercel.com
2. **Click "New Project"**
3. **Import GitHub Repository**: Select `naija-conflict-tracker`
4. **Configure Framework**:
   - Framework Preset: Next.js
   - Root Directory: `./frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`
5. **Add Environment Variables**:
   - `NEXT_PUBLIC_API_URL`: `https://your-railway-app.railway.app`
   - `NEXT_PUBLIC_MAPBOX_TOKEN`: `your-mapbox-token`
6. **Deploy**: Click Deploy!

### 3. Connect Frontend to Backend

1. **Get Railway URL**: After Railway deployment, copy your app URL
2. **Update Vercel**: In Vercel dashboard → Settings → Environment Variables:
   - `NEXT_PUBLIC_API_URL`: `https://your-actual-railway-url.railway.app`
3. **Redeploy**: Click "Redeploy" in Vercel

## 🎯 Post-Deployment Testing

### Test Backend
```bash
curl https://your-app.railway.app/health
curl https://your-app.railway.app/api/v1/conflicts/summary/overview
```

### Test Frontend
- Visit: `https://your-app.vercel.app`
- Check if API calls work
- Verify maps display (with Mapbox token)

## 📊 Import Your Data

### Option 1: Railway Shell
1. In Railway dashboard → Your service → "Shell" tab
2. Run:
```bash
cd backend
python scripts/import_excel.py --file "path/to/your/excel/file.xlsx"
```

### Option 2: API Upload
Use the API endpoints to upload data programmatically.

## 🔧 Configure Mapbox (Optional but Recommended)

1. **Get Free Token**: Go to https://mapbox.com
2. **Add to Vercel**: In Vercel dashboard → Settings → Environment Variables:
   - `NEXT_PUBLIC_MAPBOX_TOKEN`: `pk.your-token-here`
3. **Redeploy Vercel**: Maps will now display properly

## 🎉 Success!

When everything is working:
- ✅ Backend API: `https://your-app.railway.app`
- ✅ Frontend: `https://your-app.vercel.app`
- ✅ Interactive maps with conflict data
- ✅ Real-time dashboard
- ✅ Mobile responsive design
- ✅ Ready for user demonstrations!

## 🔄 Future Updates

### Update Backend
1. Push changes to GitHub
2. Go to Railway dashboard
3. Click "Deploy"

### Update Frontend  
1. Push changes to GitHub
2. Go to Vercel dashboard
3. Click "Redeploy"

## 💡 Pro Tips

- **Start with Railway first** - get the backend URL before configuring Vercel
- **Test API endpoints** before connecting frontend
- **Get Mapbox token early** for better map visualization
- **Use Railway logs** for debugging backend issues
- **Use Vercel Analytics** to monitor frontend performance

---

**🚀 Your Nigeria Conflict Tracker will be live in under 10 minutes with this simple approach!**

No GitHub Actions, no secret management, just direct platform deployment.
