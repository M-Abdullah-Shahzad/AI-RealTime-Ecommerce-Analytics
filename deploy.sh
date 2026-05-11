#!/bin/bash
# BDA Analytics Platform - Docker Deployment Script
# Usage: ./deploy.sh [command]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="bda-analytics"
IMAGE_NAME="bda-analytics"
CONTAINER_APP="bda-analytics-app"
COMPOSE_FILE="docker-compose.yml"

# Helper functions
print_header() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        echo "Download from: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    print_success "Docker installed"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    print_success "Docker Compose installed"
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        echo "Please start Docker Desktop or Docker daemon"
        exit 1
    fi
    print_success "Docker daemon is running"
    
    # Check disk space
    AVAILABLE_SPACE=$(df . | awk 'NR==2 {print $4}')
    if [ "$AVAILABLE_SPACE" -lt 10485760 ]; then
        print_warning "Less than 10GB available disk space"
    else
        print_success "Sufficient disk space available"
    fi
    
    echo ""
}

# Build Docker image
build_image() {
    print_header "Building Docker Image"
    
    if [ ! -f "Dockerfile" ]; then
        print_error "Dockerfile not found"
        exit 1
    fi
    
    docker-compose build --no-cache bda-app
    
    if [ $? -eq 0 ]; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
    echo ""
}

# Start services
start_services() {
    print_header "Starting Services"
    
    echo "Starting Zookeeper..."
    docker-compose up -d zookeeper
    
    echo "Waiting for Zookeeper to be healthy..."
    sleep 5
    
    echo "Starting Kafka..."
    docker-compose up -d kafka
    
    echo "Waiting for Kafka to be healthy..."
    sleep 10
    
    echo "Starting BDA Application..."
    docker-compose up -d bda-app
    
    echo "Waiting for dashboard to be ready..."
    sleep 15
    
    print_success "All services started"
    echo ""
}

# Stop services
stop_services() {
    print_header "Stopping Services"
    
    docker-compose stop
    
    print_success "All services stopped"
    echo ""
}

# View logs
view_logs() {
    print_header "Application Logs"
    
    if [ -z "$1" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$1"
    fi
}

# View status
view_status() {
    print_header "Service Status"
    
    docker-compose ps
    echo ""
    
    print_header "Docker Stats"
    docker stats --no-stream
}

# Clean up
cleanup() {
    print_header "Cleaning Up"
    
    read -p "Remove all containers and volumes? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        print_success "Cleanup complete"
    fi
    echo ""
}

# Full deployment
deploy() {
    print_header "BDA Analytics Platform - Full Deployment"
    
    check_prerequisites
    build_image
    start_services
    
    print_header "🎉 Deployment Complete!"
    echo ""
    echo "Services are running at:"
    echo -e "${GREEN}  Dashboard: http://localhost:8501${NC}"
    echo -e "${GREEN}  Kafka: localhost:9092${NC}"
    echo -e "${GREEN}  Zookeeper: localhost:2181${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Open http://localhost:8501 in your browser"
    echo "  2. View logs: ./deploy.sh logs"
    echo "  3. Check status: ./deploy.sh status"
    echo "  4. Stop services: ./deploy.sh stop"
    echo ""
}

# Usage information
show_usage() {
    cat << EOF
${BLUE}BDA Analytics Platform - Docker Deployment Script${NC}

${GREEN}Usage:${NC}
    ./deploy.sh [command]

${GREEN}Commands:${NC}
    deploy              Full deployment (build + start)
    build               Build Docker image only
    start               Start all services
    stop                Stop all services
    restart             Restart all services
    logs [service]      View logs (optionally for specific service)
    status              View service status and stats
    clean               Remove containers and volumes
    shell               Open bash shell in app container
    help                Show this help message

${GREEN}Examples:${NC}
    ./deploy.sh deploy              # Full deployment
    ./deploy.sh logs                # View all logs
    ./deploy.sh logs bda-app        # View app logs only
    ./deploy.sh status              # Check status
    ./deploy.sh clean               # Clean up everything

${YELLOW}Requirements:${NC}
    • Docker (https://www.docker.com/products/docker-desktop)
    • Docker Compose (usually included with Docker Desktop)
    • 8GB RAM minimum
    • 10GB disk space

EOF
}

# Main script logic
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    build)
        check_prerequisites
        build_image
        ;;
    start)
        check_prerequisites
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        start_services
        ;;
    logs)
        view_logs "$2"
        ;;
    status)
        view_status
        ;;
    clean)
        cleanup
        ;;
    shell)
        print_header "Opening Shell in BDA App Container"
        docker-compose exec bda-app bash
        ;;
    help)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
