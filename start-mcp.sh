#!/bin/bash

# Optimized MCP Server Startup Script
# Usage: ./start-mcp.sh [--port PORT] [--role ROLE] [--help]

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  echo "Usage: ./start-mcp.sh [--port PORT] [--role ROLE]"
  echo "Starts the MXCP server with clean stdio output for LLM integration."
  echo ""
  echo "Options:"
  echo "  --port PORT    Port to run the server on (default: 8462)"
  echo "  --role ROLE    User role context: 'guest' or 'admin' (for documentation/demo only; not enforced)"
  echo "  --help         Show this help message"
  echo ""
  echo "If .env/bin/activate exists, it will be sourced."
  exit 0
fi

# Default values
PORT=8462
ROLE="guest"

# Parse arguments (role is for documentation/demo only)
while [[ $# -gt 0 ]]; do
  case $1 in
    --port)
      PORT="$2"
      shift 2
      ;;
    --role)
      ROLE="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# Activate virtual environment if present
if [ -f .env/bin/activate ]; then
  source .env/bin/activate
fi

# Start server with all warnings and debug output suppressed
exec env PYTHONWARNINGS=ignore mxcp serve --port $PORT --transport stdio 2>/dev/null 