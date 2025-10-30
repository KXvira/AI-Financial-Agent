#!/bin/bash
# Phase 5 Production Deployment Script

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║           🚀 Phase 5: Production Deployment Script 🚀                ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"

# Configuration
PROJECT_NAME="finagent"
DOCKER_COMPOSE_FILE="docker-compose.production.yml"
ENV_FILE=".env.production"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Check prerequisites
echo ""
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi
print_success "Docker is installed"

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    exit 1
fi
print_success "Docker Compose is installed"

# Check environment file
echo ""
echo "🔧 Checking environment configuration..."

if [ ! -f "$ENV_FILE" ]; then
    print_warning "Production environment file not found"
    print_info "Creating from template..."
    
    cat > "$ENV_FILE" << EOF
# Production Environment Configuration
ENVIRONMENT=production

# MongoDB
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGO_DB=financial_agent

# Gemini API
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash

# JWT Security
JWT_SECRET=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# API Keys
API_KEYS=$(openssl rand -hex 16),$(openssl rand -hex 16)

# Redis
REDIS_URL=redis://redis:6379/0

# Monitoring
GRAFANA_USER=admin
GRAFANA_PASSWORD=$(openssl rand -base64 12)

# Sentry (Optional)
SENTRY_DSN=

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
EOF
    
    print_success "Environment file created: $ENV_FILE"
    print_warning "Please edit $ENV_FILE with your actual credentials"
    print_info "Then run this script again"
    exit 0
fi

print_success "Environment file found"

# Load environment
set -a
source "$ENV_FILE"
set +a

# Build Docker images
echo ""
echo "🔨 Building Docker images..."

docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache

if [ $? -eq 0 ]; then
    print_success "Docker images built successfully"
else
    print_error "Failed to build Docker images"
    exit 1
fi

# Stop existing containers
echo ""
echo "🛑 Stopping existing containers..."

docker-compose -f "$DOCKER_COMPOSE_FILE" down

print_success "Existing containers stopped"

# Start services
echo ""
echo "🚀 Starting services..."

docker-compose -f "$DOCKER_COMPOSE_FILE" up -d

if [ $? -eq 0 ]; then
    print_success "Services started successfully"
else
    print_error "Failed to start services"
    exit 1
fi

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Health checks
echo ""
echo "🏥 Running health checks..."

# Check Backend
print_info "Checking Backend..."
for i in {1..30}; do
    if curl -f http://localhost:8000/api/ocr/health &> /dev/null; then
        print_success "Backend is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Backend health check failed"
        docker-compose -f "$DOCKER_COMPOSE_FILE" logs backend
        exit 1
    fi
    sleep 2
done

# Check Redis
print_info "Checking Redis..."
if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T redis redis-cli ping | grep -q PONG; then
    print_success "Redis is healthy"
else
    print_warning "Redis health check failed"
fi

# Check Nginx
print_info "Checking Nginx..."
if curl -f http://localhost:80 &> /dev/null; then
    print_success "Nginx is healthy"
else
    print_warning "Nginx health check failed (normal if SSL not configured)"
fi

# Display service status
echo ""
echo "📊 Service Status:"
echo "─────────────────────────────────────────────────────────────"
docker-compose -f "$DOCKER_COMPOSE_FILE" ps

# Display access information
echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    🎉 Deployment Successful! 🎉                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Service URLs:"
echo "   • API:            http://localhost:8000"
echo "   • API Docs:       http://localhost:8000/docs"
echo "   • ReDoc:          http://localhost:8000/redoc"
echo "   • Health Check:   http://localhost:8000/api/ocr/health"
echo "   • Prometheus:     http://localhost:9090"
echo "   • Grafana:        http://localhost:3000"
echo ""
echo "🔑 Default Credentials:"
echo "   • Grafana:        admin / ${GRAFANA_PASSWORD:-admin}"
echo ""
echo "📝 Useful Commands:"
echo "   • View logs:      docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
echo "   • Stop services:  docker-compose -f $DOCKER_COMPOSE_FILE down"
echo "   • Restart:        docker-compose -f $DOCKER_COMPOSE_FILE restart"
echo "   • Shell access:   docker-compose -f $DOCKER_COMPOSE_FILE exec backend bash"
echo ""
echo "📖 Next Steps:"
echo "   1. Configure SSL certificates for production"
echo "   2. Set up domain name and DNS"
echo "   3. Configure monitoring alerts"
echo "   4. Set up backup strategy"
echo "   5. Review security settings"
echo ""
