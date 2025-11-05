#!/bin/bash

# FineData Docker Compose Startup Script
# This script helps you quickly start the entire FineData stack using Docker Compose

set -e

echo "🚀 Starting FineData with Docker Compose..."

# Check if docker and docker-compose are installed
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env with your configuration before running in production!"
fi

# Build and start services
echo "🏗️  Building and starting services..."
if [ "$1" = "prod" ] || [ "$1" = "production" ]; then
    echo "🌟 Starting in production mode with nginx..."
    docker-compose --profile production up --build -d
    echo ""
    echo "✅ FineData production stack is running!"
    echo ""
    echo "🌐 Frontend: https://localhost"
    echo "🔌 Backend API: https://localhost/api/v1"
    echo "📚 API Docs: https://localhost/api/v1/docs"
else
    echo "🛠️  Starting in development mode..."
    docker-compose up --build -d
    echo ""
    echo "✅ FineData development stack is running!"
    echo ""
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔌 Backend API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
fi

echo ""
echo "📊 View logs with: docker-compose logs -f [service-name]"
echo "🛑 Stop services with: docker-compose down"
echo "🔄 Restart service with: docker-compose restart [service-name]"

# Wait a bit for services to be ready
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are healthy
echo "🏥 Checking service health..."
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ API service is healthy"
else
    echo "⚠️  API service is still starting..."
fi

if curl -f http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ Web service is healthy"
else
    echo "⚠️  Web service is still starting..."
fi

echo ""
echo "🎉 FineData is ready! Open http://localhost:3000 in your browser."
