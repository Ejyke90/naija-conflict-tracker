#!/bin/bash

# Nigeria Conflict Tracker - Quick Setup Script
# This script helps you get the project running locally

set -e

echo "🇳🇬 Nigeria Conflict Tracker - Setup Script"
echo "=========================================="

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
}

# Create environment files
setup_environment() {
    echo "🔧 Setting up environment files..."
    
    # Backend .env
    if [ ! -f "backend/.env" ]; then
        cat > backend/.env << EOF
# Database (will be provided by Docker)
DATABASE_URL=postgresql://postgres:password@localhost:5432/conflict_tracker

# Redis (will be provided by Docker)
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=4320

# CORS
ALLOWED_HOSTS=["http://localhost:3000", "http://localhost:8000"]

# External APIs (optional)
TWITTER_BEARER_TOKEN=your-twitter-bearer-token
MAPBOX_ACCESS_TOKEN=your-mapbox-access-token
EOF
        echo "✅ Created backend/.env"
    else
        echo "✅ backend/.env already exists"
    fi
    
    # Frontend .env.local
    if [ ! -f "frontend/.env.local" ]; then
        cat > frontend/.env.local << EOF
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Mapbox (required for maps)
NEXT_PUBLIC_MAPBOX_TOKEN=your-mapbox-token-here

# App Configuration
NEXT_PUBLIC_APP_NAME=Nigeria Conflict Tracker
EOF
        echo "✅ Created frontend/.env.local"
    else
        echo "✅ frontend/.env.local already exists"
    fi
}

# Build and start services
start_services() {
    echo "🚀 Building and starting services..."
    
    # Build and start with Docker Compose
    docker-compose up --build -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        echo "✅ Services are running"
    else
        echo "❌ Some services failed to start. Check 'docker-compose logs' for details."
        exit 1
    fi
}

# Run database migrations
setup_database() {
    echo "🗄️ Setting up database..."
    
    # Wait for database to be ready
    echo "⏳ Waiting for database to be ready..."
    for i in {1..30}; do
        if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
            echo "✅ Database is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "❌ Database failed to start"
            exit 1
        fi
        sleep 2
    done
    
    # The schema is automatically created by the init script
    echo "✅ Database schema initialized"
}

# Install frontend dependencies
setup_frontend() {
    echo "📦 Installing frontend dependencies..."
    
    # Check if node_modules exists, if not install
    if [ ! -d "frontend/node_modules" ]; then
        docker-compose exec frontend npm install
        echo "✅ Frontend dependencies installed"
    else
        echo "✅ Frontend dependencies already installed"
    fi
}

# Test the setup
test_setup() {
    echo "🧪 Testing the setup..."
    
    # Test backend health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy"
    else
        echo "❌ Backend health check failed"
    fi
    
    # Test frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is accessible"
    else
        echo "❌ Frontend health check failed"
    fi
    
    # Test API
    if curl -f http://localhost:8000/api/v1/conflicts/summary/overview > /dev/null 2>&1; then
        echo "✅ API is working"
    else
        echo "❌ API test failed"
    fi
}

# Print next steps
print_next_steps() {
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "🌐 Access your application:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   API Documentation: http://localhost:8000/docs"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Get a Mapbox token and add it to frontend/.env.local"
    echo "   2. Import your Excel data: python scripts/import_excel.py"
    echo "   3. Configure external API keys in backend/.env"
    echo "   4. Deploy to production: Railway + Vercel"
    echo ""
    echo "📚 Useful commands:"
    echo "   View logs: docker-compose logs -f"
    echo "   Stop services: docker-compose down"
    echo "   Restart services: docker-compose restart"
    echo "   Access database: docker-compose exec postgres psql -U postgres -d conflict_tracker"
    echo ""
    echo "🚀 Ready to build Nigeria's conflict tracking platform!"
}

# Main execution
main() {
    check_prerequisites
    setup_environment
    start_services
    setup_database
    setup_frontend
    test_setup
    print_next_steps
}

# Run main function
main "$@"
