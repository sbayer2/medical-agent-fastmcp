#!/usr/bin/env python3
"""Test FastAgent initialization and configuration"""

import asyncio
import os
import sys
import logging
from mcp_agent.core.fastagent import FastAgent

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_fastagent():
    """Test FastAgent with minimal configuration"""
    
    # Check environment
    logger.info("=== Environment Check ===")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Files in directory: {os.listdir('.')}")
    
    # Check for required files
    config_files = ['fastagent.config.yaml', 'fastagent.secrets.yaml']
    for f in config_files:
        if os.path.exists(f):
            logger.info(f"✓ Found {f}")
        else:
            logger.warning(f"✗ Missing {f}")
    
    # Check environment variables
    env_vars = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'STRIPE_SECRET_KEY']
    for var in env_vars:
        if os.getenv(var):
            logger.info(f"✓ {var} is set (length: {len(os.getenv(var))})")
        else:
            logger.warning(f"✗ {var} is not set")
    
    # Test 1: Create FastAgent without config
    logger.info("\n=== Test 1: FastAgent without config ===")
    try:
        fast1 = FastAgent("Test Agent")
        logger.info("✓ Created FastAgent without config")
    except Exception as e:
        logger.error(f"✗ Failed to create FastAgent: {e}")
        return
    
    # Test 2: Create FastAgent with config
    logger.info("\n=== Test 2: FastAgent with config ===")
    try:
        fast2 = FastAgent("Test Agent", config_path="fastagent.config.yaml")
        logger.info("✓ Created FastAgent with config")
    except Exception as e:
        logger.error(f"✗ Failed to create FastAgent with config: {e}")
    
    # Test 3: Try to run the agent
    logger.info("\n=== Test 3: Running FastAgent ===")
    try:
        # Create a minimal agent
        fast = FastAgent("Test Medical Agent")
        
        @fast.agent(
            name="test_agent",
            instruction="You are a test agent. Just say hello.",
            servers=[],  # No MCP servers
            model="claude-3-5-sonnet-20241022"
        )
        async def test_agent():
            pass
        
        async with fast.run() as agent:
            logger.info("✓ Agent started successfully")
            response = await agent.send("Hello, can you hear me?")
            logger.info(f"✓ Got response: {response[:100]}...")
            
    except Exception as e:
        logger.error(f"✗ Failed to run agent: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    logger.info("Starting FastAgent tests...")
    asyncio.run(test_fastagent())
