#!/bin/bash

echo "🚀 Setting up AI Boilerplate..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker is installed"

# Create .env files from examples
echo "📝 Creating environment files..."

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env"
else
    echo "⚠️  backend/.env already exists, skipping..."
fi

if [ ! -f frontend/.env ]; then
    cp frontend/.env.example frontend/.env
    echo "✅ Created frontend/.env"
else
    echo "⚠️  frontend/.env already exists, skipping..."
fi

echo ""
echo "⚠️  IMPORTANT: Edit the .env files with your API keys before starting!"
echo "   - backend/.env: Add your CEREBRAS_API_KEY and VOYAGE_API_KEY"
echo "   - frontend/.env: Configure NEXT_PUBLIC_API_URL if needed"
echo ""

# Build and start services
echo "🐳 Starting Docker services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Setup complete! Services are running:"
    echo ""
    echo "   Frontend:  http://localhost:3000"
    echo "   Backend:   http://localhost:8000"
    echo "   API Docs:  http://localhost:8000/docs"
    echo "   Weaviate:  http://localhost:8080"
    echo ""
    echo "📚 Next steps:"
    echo "   1. Edit backend/.env with your API keys"
    echo "   2. Edit frontend/.env if needed"
    echo "   3. Restart services: docker-compose restart"
    echo "   4. View logs: docker-compose logs -f"
    echo ""
else
    echo "❌ Some services failed to start. Check logs with: docker-compose logs"
    exit 1
fi
