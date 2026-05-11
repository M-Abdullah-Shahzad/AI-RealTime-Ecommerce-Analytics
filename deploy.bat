@echo off
REM BDA Analytics Platform - Docker Deployment Script (Windows)
REM Usage: deploy.bat [command]

setlocal enabledelayedexpansion

REM Colors (using findstr for colored output workaround in Windows)
REM Note: Windows batch doesn't support true ANSI colors in older versions
REM Using echo with findstr workaround for visual effects

set "PROJECT_NAME=bda-analytics"
set "IMAGE_NAME=bda-analytics"
set "CONTAINER_APP=bda-analytics-app"
set "COMPOSE_FILE=docker-compose.yml"

REM ============================================================================
REM Helper Functions
REM ============================================================================

:print_header
echo.
echo ========================================================
echo %~1
echo ========================================================
goto :eof

:print_success
echo [OK] %~1
goto :eof

:print_error
echo [ERROR] %~1
goto :eof

:print_warning
echo [WARNING] %~1
goto :eof

REM ============================================================================
REM Check Prerequisites
REM ============================================================================

:check_prerequisites
call :print_header "Checking Prerequisites"

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker is not installed"
    echo Download from: https://www.docker.com/products/docker-desktop
    exit /b 1
)
call :print_success "Docker installed"

REM Check Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker Compose is not installed"
    exit /b 1
)
call :print_success "Docker Compose installed"

REM Check Docker daemon
docker info >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker daemon is not running"
    echo Please start Docker Desktop
    exit /b 1
)
call :print_success "Docker daemon is running"

echo.
goto :eof

REM ============================================================================
REM Build Docker Image
REM ============================================================================

:build_image
call :print_header "Building Docker Image"

if not exist "Dockerfile" (
    call :print_error "Dockerfile not found"
    exit /b 1
)

docker-compose build --no-cache bda-app
if errorlevel 1 (
    call :print_error "Failed to build Docker image"
    exit /b 1
)

call :print_success "Docker image built successfully"
echo.
goto :eof

REM ============================================================================
REM Start Services
REM ============================================================================

:start_services
call :print_header "Starting Services"

echo Starting Zookeeper...
docker-compose up -d zookeeper

echo Waiting for Zookeeper to be healthy...
timeout /t 5 /nobreak >nul

echo Starting Kafka...
docker-compose up -d kafka

echo Waiting for Kafka to be healthy...
timeout /t 10 /nobreak >nul

echo Starting BDA Application...
docker-compose up -d bda-app

echo Waiting for dashboard to be ready...
timeout /t 15 /nobreak >nul

call :print_success "All services started"
echo.
goto :eof

REM ============================================================================
REM Stop Services
REM ============================================================================

:stop_services
call :print_header "Stopping Services"

docker-compose stop

call :print_success "All services stopped"
echo.
goto :eof

REM ============================================================================
REM View Logs
REM ============================================================================

:view_logs
call :print_header "Application Logs"

if "%~1"=="" (
    docker-compose logs -f
) else (
    docker-compose logs -f %~1
)
goto :eof

REM ============================================================================
REM View Status
REM ============================================================================

:view_status
call :print_header "Service Status"

docker-compose ps
echo.

call :print_header "Docker Stats"
docker stats --no-stream
goto :eof

REM ============================================================================
REM Cleanup
REM ============================================================================

:cleanup
call :print_header "Cleaning Up"

set /p confirm="Remove all containers and volumes? (y/n): "
if /i "%confirm%"=="y" (
    docker-compose down -v
    call :print_success "Cleanup complete"
) else (
    echo Cleanup cancelled
)
echo.
goto :eof

REM ============================================================================
REM Full Deployment
REM ============================================================================

:deploy
call :print_header "BDA Analytics Platform - Full Deployment"

call :check_prerequisites
if errorlevel 1 exit /b 1

call :build_image
if errorlevel 1 exit /b 1

call :start_services
if errorlevel 1 exit /b 1

call :print_header "=== DEPLOYMENT COMPLETE ==="
echo.
echo Services are running at:
echo   Dashboard: http://localhost:8501
echo   Kafka: localhost:9092
echo   Zookeeper: localhost:2181
echo.
echo Next steps:
echo   1. Open http://localhost:8501 in your browser
echo   2. View logs: deploy.bat logs
echo   3. Check status: deploy.bat status
echo   4. Stop services: deploy.bat stop
echo.
goto :eof

REM ============================================================================
REM Show Usage
REM ============================================================================

:show_usage
echo.
echo BDA Analytics Platform - Docker Deployment Script
echo.
echo Usage:
echo     deploy.bat [command]
echo.
echo Commands:
echo     deploy              Full deployment (build + start)
echo     build               Build Docker image only
echo     start               Start all services
echo     stop                Stop all services
echo     restart             Restart all services
echo     logs [service]      View logs (optionally for specific service)
echo     status              View service status and stats
echo     clean               Remove containers and volumes
echo     shell               Open bash shell in app container
echo     help                Show this help message
echo.
echo Examples:
echo     deploy.bat deploy              # Full deployment
echo     deploy.bat logs                # View all logs
echo     deploy.bat logs bda-app        # View app logs only
echo     deploy.bat status              # Check status
echo     deploy.bat clean               # Clean up everything
echo.
echo Requirements:
echo     * Docker Desktop (https://www.docker.com/products/docker-desktop)
echo     * Docker Compose (usually included with Docker Desktop)
echo     * 8GB RAM minimum
echo     * 10GB disk space
echo.
goto :eof

REM ============================================================================
REM Main Entry Point
REM ============================================================================

:main
if "%~1"=="" (
    call :deploy
) else if /i "%~1"=="deploy" (
    call :deploy
) else if /i "%~1"=="build" (
    call :check_prerequisites
    call :build_image
) else if /i "%~1"=="start" (
    call :check_prerequisites
    call :start_services
) else if /i "%~1"=="stop" (
    call :stop_services
) else if /i "%~1"=="restart" (
    call :stop_services
    timeout /t 2 /nobreak >nul
    call :start_services
) else if /i "%~1"=="logs" (
    call :view_logs "%~2"
) else if /i "%~1"=="status" (
    call :view_status
) else if /i "%~1"=="clean" (
    call :cleanup
) else if /i "%~1"=="shell" (
    call :print_header "Opening Shell in BDA App Container"
    docker-compose exec bda-app bash
) else if /i "%~1"=="help" (
    call :show_usage
) else (
    call :print_error "Unknown command: %~1"
    echo.
    call :show_usage
    exit /b 1
)

endlocal
