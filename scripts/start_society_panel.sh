#!/usr/bin/env bash

################################################################################
#                                                                              #
#                    SOCIETY-PANEL Unified Startup Script                      #
#                           (macOS/Linux Version)                              #
#                                                                              #
################################################################################
#
# Description:
#   This script automates the setup and launch of both the backend and frontend
#   services for the SOCIETY-PANEL. It handles dependency checks, virtual 
#   environment management, and graceful shutdown.
#
# Usage:
#   ./start_society_panel.sh
#
# Requirements:
#   - Python 3.11 or higher
#   - Node.js and npm
#   - Internet connection (for package installation)
#
# Author:  SOCIETY-PANEL Team
# Version: 3.0
#
################################################################################

# ==============================================================================
# Shell Options
# ==============================================================================

set -e          # Exit immediately if a command exits with a non-zero status
set -o pipefail # Exit if any command in a pipeline fails

# ==============================================================================
# Global Configuration
# ==============================================================================

# Directory Paths
readonly ROOT_DIR="$(pwd)"
readonly BACKEND_DIR="society-panel/backend"
readonly FRONTEND_DIR="society-panel/frontend"

# Server Ports
readonly BACKEND_PORT=8001
readonly FRONTEND_PORT=5174

# Terminal Color Codes
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly NC='\033[0m'  # No Color

# Process Tracking Variables
BACKEND_PID=""
FRONTEND_PID=""

# ==============================================================================
# Utility Functions
# ==============================================================================

##
# @brief Print an info message with green [INFO] prefix
# @param $1 Message to print
##
print_info() { echo -e "${GREEN}[INFO]${NC} $1"; }

##
# @brief Print a warning message with yellow [WARN] prefix
# @param $1 Message to print
##
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

##
# @brief Print an error message with red [ERROR] prefix
# @param $1 Message to print
##
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

##
# @brief Gracefully shutdown all services and cleanup resources
# @details Handles SIGINT and SIGTERM signals to ensure proper cleanup
##
cleanup() {
    print_info "Caught exit signal. Shutting down all services..."

    # Terminate backend process
    if [[ -n "$BACKEND_PID" ]] && kill "$BACKEND_PID" > /dev/null 2>&1; then
        print_info "Backend service (PID: $BACKEND_PID) has been sent a shutdown signal."
    fi

    # Terminate frontend process
    if [[ -n "$FRONTEND_PID" ]] && kill "$FRONTEND_PID" > /dev/null 2>&1; then
        print_info "Frontend service (PID: $FRONTEND_PID) has been sent a shutdown signal."
    fi

    sleep 1

    # Shutdown Ray cluster if running
    if ray status > /dev/null 2>&1; then
        print_info "Shutting down Ray cluster..."
        ray stop
        print_info "Ray cluster has been shut down."
    fi

    echo "Cleanup complete!"
    exit 0
}

# Register signal handlers for graceful shutdown
trap cleanup SIGINT SIGTERM

# ==============================================================================
# Pre-cleanup: Stop Lingering Services
# ==============================================================================

print_info "Performing pre-cleanup to stop any lingering services..."

# Kill any processes occupying the required ports
lsof -ti :"$BACKEND_PORT" | xargs kill -9 > /dev/null 2>&1 || true
lsof -ti :"$FRONTEND_PORT" | xargs kill -9 > /dev/null 2>&1 || true

# Stop Ray cluster if running
if ray status > /dev/null 2>&1; then
    ray stop
fi

print_info "Pre-cleanup finished."

# ==============================================================================
# Clean Workspace and Logs
# ==============================================================================

print_info "Cleaning backend workspace and logs directories..."

# Clean entire workspace directory contents
if [ -d "$BACKEND_DIR/workspace" ]; then
    rm -rf "$BACKEND_DIR/workspace"/*
    print_info "  - Cleaned: workspace/"
fi

# Clean backend logs directory (including all subdirectories)
if [ -d "$BACKEND_DIR/logs" ]; then
    find "$BACKEND_DIR/logs" -mindepth 1 -delete
    # Recreate subdirectory structure
    mkdir -p "$BACKEND_DIR/logs/framework" "$BACKEND_DIR/logs/app"
    print_info "  - Cleaned: logs/ (framework/, app/)"
fi

print_info "Workspace and logs cleanup finished."

# ==============================================================================
# Backend Service Setup and Launch
# ==============================================================================

print_info "Preparing backend service..."
cd "$BACKEND_DIR" || { print_error "Backend directory not found: $BACKEND_DIR"; exit 1; }

# Check uv availability
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Sync dependencies from workspace lockfile
print_info "Syncing dependencies with uv..."
uv sync --project "$ROOT_DIR" --all-extras --group panel

# Launch backend server
print_info "Starting FastAPI backend in the background (Port: $BACKEND_PORT)..."
uv run --project "$ROOT_DIR" uvicorn app.main:app --reload --host 0.0.0.0 --port "$BACKEND_PORT" &
BACKEND_PID=$!
cd - > /dev/null

# ==============================================================================
# Frontend Service Setup and Launch
# ==============================================================================

print_info "Preparing frontend service..."
cd "$FRONTEND_DIR" || { print_error "Frontend directory not found: $FRONTEND_DIR"; exit 1; }

# Install/update frontend dependencies
if [ ! -d "node_modules" ] || [ "package.json" -nt "package-lock.json" ]; then
    print_info "Frontend dependencies need to be installed or updated. Running npm install..."
    npm install
fi

# Launch frontend dev server
print_info "Starting Vite frontend dev server in the background (Port: $FRONTEND_PORT)..."
npm run dev -- --port "$FRONTEND_PORT" --host &
FRONTEND_PID=$!
cd - > /dev/null

# ==============================================================================
# Startup Complete - Wait for Termination
# ==============================================================================

print_info "=================================================="
print_info "SOCIETY-PANEL has been launched!"
print_info "  - Backend API available at: http://localhost:$BACKEND_PORT"
print_info "  - Frontend UI accessible at: http://localhost:$FRONTEND_PORT"
print_info "Press Ctrl+C to shut down all services."
print_info "=================================================="

wait
