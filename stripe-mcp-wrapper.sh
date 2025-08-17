#!/bin/bash
# stripe-mcp-wrapper.sh - Wrapper for Stripe MCP in Docker

# Source environment variables from mounted .zshrc
if [ -f "/root/.zshrc" ]; then
    source "/root/.zshrc" 2>/dev/null
fi

# Also check for environment variable
if [ -z "$STRIPE_SECRET_KEY" ] && [ -n "$STRIPE_API_KEY" ]; then
    STRIPE_SECRET_KEY="$STRIPE_API_KEY"
fi

# Validate Stripe key
if [ -z "$STRIPE_SECRET_KEY" ]; then
    echo "Error: STRIPE_SECRET_KEY not found" >&2
    echo "Please ensure your .zshrc is mounted or STRIPE_API_KEY is set" >&2
    exit 1
fi

if [[ ! "$STRIPE_SECRET_KEY" =~ ^(sk_|rk_) ]]; then
    echo "Error: Invalid STRIPE_SECRET_KEY format" >&2
    exit 1
fi

# Export for child processes
export STRIPE_API_KEY="${STRIPE_SECRET_KEY}"

# Launch Stripe MCP server with all tools
exec npx -y @stripe/mcp --tools=all --api-key="$STRIPE_SECRET_KEY"
