#!/bin/bash
# Startup script to ensure MCP servers are available

echo "Starting Medical Agent SaaS..."

# Check if MCP filesystem server is installed globally
MCP_GLOBAL_PATH=$(npm list -g @modelcontextprotocol/server-filesystem --parseable 2>/dev/null | head -1)

if [ -z "$MCP_GLOBAL_PATH" ]; then
    echo "MCP filesystem server not found globally, checking local..."
    # Check local node_modules
    if [ ! -d "/app/node_modules/@modelcontextprotocol/server-filesystem" ]; then
        echo "Installing MCP filesystem server locally..."
        npm install @modelcontextprotocol/server-filesystem
    fi
    MCP_FS_BIN="/app/node_modules/.bin/mcp-server-filesystem"
else
    echo "Found global MCP filesystem server at: $MCP_GLOBAL_PATH"
    MCP_FS_BIN="$MCP_GLOBAL_PATH/bin/index.js"
fi

echo "MCP filesystem server binary: $MCP_FS_BIN"

# Test if the server can be executed
if [ -f "$MCP_FS_BIN" ]; then
    echo "MCP filesystem server found and executable"
else
    echo "Warning: MCP filesystem server binary not found at $MCP_FS_BIN"
    # Try using npx as fallback
    MCP_FS_BIN="npx @modelcontextprotocol/server-filesystem"
fi

# Update the config file with the correct path
cat > /app/fastagent.config.yaml << EOF
# FastAgent Configuration File for Medical SaaS

# Default Model Configuration  
default_model: claude-3-5-sonnet-20241022

# Logging and Console Configuration
logger:
    progress_display: true
    show_chat: true
    show_tools: true
    truncate_tools: true

# MCP Servers Configuration
mcp:
    servers:
        # Filesystem server - for medical document access
        filesystem:
            command: "npx"
            args: ["-y", "@modelcontextprotocol/server-filesystem", "/app/medical_files_data"]
            
    # Agent configuration
    agents:
        medical_analyzer:
            servers: ["filesystem"]
            model: "claude-3-5-sonnet-20241022"
EOF

echo "Configuration updated"

# Start the API server
exec python api_server.py
