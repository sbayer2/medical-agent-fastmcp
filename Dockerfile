FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    bash \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for MCP servers
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install -y nodejs

# Verify npm and npx are available
RUN node --version && npm --version && npx --version

# Install MCP servers globally
RUN npm install -g @modelcontextprotocol/server-filesystem

# Test that the MCP server can be run with npx
RUN npx -y @modelcontextprotocol/server-filesystem --help || echo "MCP filesystem server test completed"

# Create symlinks for easier access (optional)
RUN ln -s /usr/bin/node /usr/local/bin/node || true

# Verify MCP servers are installed
RUN which mcp-server-filesystem || echo "Filesystem server not found in PATH"

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Verify fast-agent-mcp is installed
RUN python -c "from mcp_agent.core.fastagent import FastAgent; print('FastAgent imported successfully')"

# Copy application files
COPY . .

# Copy secrets file if it exists
COPY fastagent.secrets.yaml /app/fastagent.secrets.yaml

# Make scripts executable
RUN chmod +x /app/stripe-mcp-wrapper.sh /app/startup.sh

# Create necessary directories
RUN mkdir -p /app/medical_files_data /app/prompts

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the startup script
CMD ["./startup.sh"]
