#!/bin/bash

# 🚀 BraveBot Complete Startup Script
# ==================================
# سكريبت شامل لتشغيل جميع خدمات BraveBot

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed!"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ "$python_version" < "3.11" ]]; then
        warning "Python 3.11+ is recommended. Current version: $python_version"
    fi
}

# Create virtual environment if it doesn't exist
setup_venv() {
    if [ ! -d "venv" ]; then
        log "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    log "Activating virtual environment..."
    source venv/bin/activate
    
    log "Upgrading pip..."
    pip install --upgrade pip
}

# Install dependencies
install_dependencies() {
    log "Installing dependencies..."
    pip install -r requirements.txt
    
    log "Installing additional monitoring dependencies..."
    pip install psutil aiohttp cryptography || warning "Some monitoring features may not work"
}

# Check environment variables
check_environment() {
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            warning ".env file not found. Creating from template..."
            cp .env.example .env
            error "Please edit .env file with your configuration before running again!"
            exit 1
        else
            error ".env file not found and no template available!"
            exit 1
        fi
    fi
    
    source .env
    
    if [ -z "$TELEGRAM_TOKEN" ]; then
        error "TELEGRAM_TOKEN not set in .env file!"
        exit 1
    fi
    
    log "Environment configuration checked ✓"
}

# Initialize database
init_database() {
    log "Initializing database..."
    python3 -c "
from core.database_manager import init_db
try:
    init_db()
    print('✅ Database initialized successfully')
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
    exit(1)
"
}

# Run tests
run_tests() {
    if [ "$1" = "test" ]; then
        log "Running tests..."
        python3 -m pytest tests/ -v --tb=short || {
            error "Tests failed!"
            exit 1
        }
        log "All tests passed ✓"
    fi
}

# Start monitoring services
start_monitoring() {
    if [ "$1" = "monitor" ]; then
        log "Starting health monitoring..."
        python3 scripts/health_monitor.py &
        MONITOR_PID=$!
        echo $MONITOR_PID > monitor.pid
        log "Monitor started with PID: $MONITOR_PID"
    fi
}

# Start backup service
start_backup() {
    if [ "$1" = "backup" ]; then
        log "Starting backup service..."
        python3 scripts/backup_system.py &
        BACKUP_PID=$!
        echo $BACKUP_PID > backup.pid
        log "Backup service started with PID: $BACKUP_PID"
    fi
}

# Start main bot
start_bot() {
    log "Starting BraveBot..."
    log "Press Ctrl+C to stop"
    
    # Create trap for cleanup
    trap cleanup EXIT
    
    python3 main.py
}

# Cleanup function
cleanup() {
    log "Shutting down services..."
    
    if [ -f "monitor.pid" ]; then
        MONITOR_PID=$(cat monitor.pid)
        kill $MONITOR_PID 2>/dev/null || true
        rm monitor.pid
        log "Health monitor stopped"
    fi
    
    if [ -f "backup.pid" ]; then
        BACKUP_PID=$(cat backup.pid)
        kill $BACKUP_PID 2>/dev/null || true
        rm backup.pid
        log "Backup service stopped"
    fi
    
    log "Cleanup completed"
}

# Main function
main() {
    echo "🤖 BraveBot Startup Script"
    echo "=========================="
    
    # Parse arguments
    RUN_TESTS=false
    START_MONITOR=false
    START_BACKUP=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --test)
                RUN_TESTS=true
                shift
                ;;
            --monitor)
                START_MONITOR=true
                shift
                ;;
            --backup)
                START_BACKUP=true
                shift
                ;;
            --all)
                RUN_TESTS=true
                START_MONITOR=true
                START_BACKUP=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --test      Run tests before starting"
                echo "  --monitor   Start health monitoring"
                echo "  --backup    Start backup service"
                echo "  --all       Enable all features"
                echo "  --help      Show this help message"
                echo ""
                exit 0
                ;;
            *)
                warning "Unknown option: $1"
                shift
                ;;
        esac
    done
    
    # Main startup sequence
    check_python
    setup_venv
    install_dependencies
    check_environment
    init_database
    
    if [ "$RUN_TESTS" = true ]; then
        run_tests test
    fi
    
    if [ "$START_MONITOR" = true ]; then
        start_monitoring monitor
    fi
    
    if [ "$START_BACKUP" = true ]; then
        start_backup backup
    fi
    
    start_bot
}

# Run main function with all arguments
main "$@"
