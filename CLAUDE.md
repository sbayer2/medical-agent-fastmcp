# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Medical Agent MCP Server platform deployed on FastMCP Cloud that provides AI-powered medical document analysis services. The system uses Claude Sonnet 4 as the primary AI model with OpenAI GPT-4o as fallback, processing various medical documents including SOAP notes, lab reports, and patient histories with live Stripe payment integration.

## Tech Stack

- **Runtime**: Python 3.12
- **Framework**: FastMCP 2.2.6+
- **Deployment**: FastMCP Cloud
- **Primary AI Model**: Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- **Fallback AI Model**: OpenAI GPT-4o (`gpt-4o`)
- **Payment Processing**: Stripe Live API
- **Protocol**: Model Context Protocol (MCP)
- **Package Management**: pip with virtual environments

## Project Structure

```
/
├── medical_mcp_server.py       # Main FastMCP server with AI analysis
├── requirements.txt           # FastMCP dependencies with AI libraries
├── test_medical_server.py     # AI functionality testing script
├── test_openai_fallback.py    # OpenAI fallback testing script
├── .env.template             # Environment variables template
├── MEDIUM_ARTICLE.md         # Development story for publication
├── README.md                 # Complete project documentation
└── CLAUDE.md                # This file - project guidance
```

## Key Components

### Medical MCP Server (medical_mcp_server.py)
- **Primary Function**: `analyze_medical_document()` - AI-powered medical analysis
- **AI Models**: Claude Sonnet 4 (primary) + OpenAI GPT-4o (fallback)
- **Billing Tiers**: Basic ($0.10), Comprehensive ($0.50), Batch ($0.05)
- **Payment Integration**: Full Stripe payment workflow with 5 tools
- **Analysis Types**: 
  - Basic: Vital signs, medications, conditions extraction
  - Comprehensive: Full clinical insights with recommendations
  - Batch: Volume processing with enterprise discounts

### AI Analysis Engine
- **System Prompts**: Tier-specific medical analysis prompts
- **Token Tracking**: Real-time usage monitoring for billing
- **Error Handling**: Graceful fallback from Claude to OpenAI
- **Response Format**: Structured JSON with medical categories
- **Medical Focus**: SOAP notes, lab reports, patient histories

### Payment Processing System
- **Stripe Integration**: Live payment processing with webhooks
- **Customer Management**: Full customer lifecycle management
- **Usage Tracking**: Per-analysis billing with volume discounts
- **Payment Flows**: Intent creation, confirmation, and processing

## Environment Variables

Required environment variables for FastMCP Cloud deployment:
- `ANTHROPIC_API_KEY` - Primary AI provider (Claude Sonnet 4)
- `OPENAI_API_KEY` - Fallback AI provider (GPT-4o) 
- `STRIPE_API_KEY` - Live payment processing

## Development Commands

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test AI functionality
python3 test_medical_server.py

# Test OpenAI fallback
python3 test_openai_fallback.py

# Verify server imports
python3 -c "from medical_mcp_server import mcp; print('✅ Server ready')"

# Run with environment variables
ANTHROPIC_API_KEY=your_key OPENAI_API_KEY=your_key python3 test_medical_server.py
```

## Live Deployment

### FastMCP Cloud Integration
```bash
# Add to Claude Desktop
claude mcp add --scope local --transport http Medical-agent-server https://medical-agent-server.fastmcp.app/mcp

# Add to Claude Code
claude mcp add Medical-agent-server https://medical-agent-server.fastmcp.app/mcp
```

### Available Tools (10 total)
**Medical Analysis:**
- `analyze_medical_document` - AI analysis with Claude Sonnet 4
- `get_patient_summary` - Patient data retrieval
- `get_available_services` - Service catalog

**Payment Processing:**
- `create_customer` - Stripe customer management
- `create_payment_intent` - Payment processing
- `confirm_payment` - Payment verification  
- `process_paid_analysis` - End-to-end paid workflow
- `get_customer_info` - Customer history

**System:**
- `calculate_billing` - Multi-tier pricing
- `health_check` - Server status

## Medical Analysis Flow

1. User provides medical document content
2. System selects AI model (Claude Sonnet 4 primary, GPT-4o fallback)
3. Tier-specific system prompt applied (basic/comprehensive/batch)
4. AI processes document with medical focus
5. Structured JSON response with extracted medical data
6. Token usage tracked for billing accuracy

## Common Development Tasks

### Adding New Medical Analysis Features
1. Update system prompts in `analyze_medical_document()` function
2. Modify billing tiers in `BILLING_TIERS` dictionary
3. Enhance medical data extraction logic
4. Test with both Claude and OpenAI models

### Testing AI Integration
- Use `test_medical_server.py` for Claude Sonnet 4 testing
- Use `test_openai_fallback.py` for GPT-4o fallback testing
- Verify environment variable configuration
- Check token usage and billing accuracy

### Debugging
- Monitor FastMCP Cloud deployment logs
- Test API endpoints via MCP protocol
- Verify Stripe webhook integration
- Check AI model response quality and token usage