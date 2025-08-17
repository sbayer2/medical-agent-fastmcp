# FastMCP Cloud Deployment Guide

## Medical Agent MCP Server

This guide helps you deploy your medical document analysis server to FastMCP Cloud.

## 🚀 What You've Built

Your FastMCP server includes:

### Core Features
- **Medical Document Analysis** (3 tiers: Basic $0.10, Comprehensive $0.50, Batch $0.05)
- **Patient Data Management** (sample data with demographics, vitals, medications)
- **Full Stripe Payment Integration** (customer creation, payment intents, confirmation)
- **Health Monitoring** (API status checks, service health)

### Available Tools (10 total)
1. `create_customer` - Create Stripe customers
2. `create_payment_intent` - Set up payments 
3. `confirm_payment` - Verify payment status
4. `process_paid_analysis` - Execute analysis after payment
5. `get_customer_info` - Retrieve customer data
6. `analyze_medical_document` - Core medical analysis
7. `get_patient_summary` - Patient data retrieval
8. `calculate_billing` - Cost calculations
9. `get_available_services` - Service catalog
10. `health_check` - System monitoring

## 📁 Files for Deployment

### Required Files
- `medical_mcp_server.py` - Main FastMCP server
- `requirements_fastmcp.txt` - Dependencies
- `.env.template` - Environment variables template

### Dependencies
```
fastmcp>=2.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
typing-extensions>=4.5.0
stripe>=5.0.0
anthropic>=0.25.0
httpx>=0.24.0
```

## 🔑 Required Environment Variables

You'll need these API keys for FastMCP Cloud:

```bash
# Stripe Payment Processing
STRIPE_API_KEY=sk_test_your_stripe_secret_key_here

# Anthropic AI (for Claude)
ANTHROPIC_API_KEY=sk-ant-your_anthropic_api_key_here

# OpenAI (optional)
OPENAI_API_KEY=sk-your_openai_api_key_here
```

## 🌐 Deployment Steps

### 1. Create GitHub Repository
```bash
# Create new repo on GitHub
# Push these files:
- medical_mcp_server.py
- requirements_fastmcp.txt (rename to requirements.txt)
- .env.template
- README.md (optional)
```

### 2. FastMCP Cloud Setup
1. Visit [fastmcp.cloud](https://fastmcp.cloud)
2. Sign in with GitHub
3. Create new project from your repo
4. Configure:
   - **Name**: `medical-agent-saas`
   - **Entrypoint**: `medical_mcp_server.py:mcp`
   - **Authentication**: Enable (recommended)

### 3. Environment Variables
In FastMCP Cloud dashboard, add:
- `STRIPE_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY` (optional)

### 4. Deploy
FastMCP Cloud will automatically:
- Clone your repository
- Install dependencies from requirements.txt
- Deploy to unique URL: `https://your-project-name.fastmcp.app/mcp`

## 📊 Usage Examples

### Payment Workflow
```python
# 1. Create customer
create_customer(email="doctor@hospital.com", name="Dr. Smith")

# 2. Create payment intent
create_payment_intent(
    customer_id="cus_xxx",
    analysis_type="comprehensive", 
    document_count=1
)

# 3. After payment confirmation
process_paid_analysis(
    payment_intent_id="pi_xxx",
    document_content="Patient presents with chest pain..."
)
```

### Direct Analysis (without payment)
```python
analyze_medical_document(
    document_content="BP 150/95, HR 88, Diabetes, Hypertension",
    analysis_type="basic"
)
```

## 🔗 Integration

Once deployed, your MCP server will be available to:
- **Claude Desktop** (with MCP configuration)
- **Cursor IDE** (with MCP integration)
- **Custom Applications** (via MCP protocol)

## 🎯 Next Steps

1. **Test locally**: `fastmcp run medical_mcp_server.py:mcp`
2. **Create GitHub repo** with required files
3. **Deploy to FastMCP Cloud**
4. **Configure environment variables**
5. **Test with Claude or Cursor**

## 🔒 Security Notes

- Use test Stripe keys for development
- Enable authentication in FastMCP Cloud
- Never commit API keys to GitHub
- Use environment variables for all secrets

Your medical analysis MCP server is now ready for professional deployment! 🏥✨