#!/bin/bash

# Nigeria Conflict Tracker - Deployment Setup Script
# This script helps you configure Railway and Vercel deployment

set -e

echo "🚀 Nigeria Conflict Tracker - Deployment Setup"
echo "=============================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "🔧 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: Nigeria Conflict Tracker MVP"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

echo ""
echo "📋 Next Steps for Deployment:"
echo ""

echo "1️⃣  Push to GitHub:"
echo "   git remote add origin <your-github-repo-url>"
echo "   git push -u origin main"
echo ""

echo "2️⃣  Setup Railway (Backend):"
echo "   • Go to https://railway.app"
echo "   • Click 'New Project' → 'Deploy from GitHub repo'"
echo "   • Select your repository"
echo "   • Add environment variables (see DEPLOYMENT_CHECKLIST.md)"
echo "   • Click 'Deploy'"
echo ""

echo "3️⃣  Setup Vercel (Frontend):"
echo "   • Go to https://vercel.com"
echo "   • Click 'New Project' → Import your GitHub repo"
echo "   • Configure environment variables:"
echo "     - NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app"
echo "     - NEXT_PUBLIC_MAPBOX_TOKEN=your-mapbox-token"
echo "   • Click 'Deploy'"
echo ""

echo "4️⃣  Update Vercel Configuration:"
echo "   • Edit frontend/vercel.json"
echo "   • Replace 'https://your-railway-app.railway.app' with your actual Railway URL"
echo ""

echo "5️⃣  Test Your Live App:"
echo "   • Backend: https://your-app.railway.app/health"
echo "   • Frontend: https://your-app.vercel.app"
echo "   • API Docs: https://your-app.railway.app/docs"
echo ""

echo "📚 Important Files:"
echo "   • DEPLOYMENT_CHECKLIST.md - Complete deployment guide"
echo "   • docs/DEPLOYMENT.md - Detailed deployment documentation"
echo "   • .github/workflows/deploy.yml - Automatic deployment setup"
echo ""

echo "🎯 Ready for Production!"
echo "   Your Nigeria Conflict Tracker is scaffolded and ready for deployment."
echo "   Follow the steps above to get it live on Railway + Vercel."
echo ""

echo "💡 Pro Tip:"
echo "   Get your free Mapbox token from https://mapbox.com for map visualizations."
echo ""
