# Medical Agent MCP Server

🏥 **Production-ready medical document analysis platform** powered by Claude Sonnet 4 and deployed on FastMCP Cloud.

## 🚀 **Live Deployment**

**FastMCP Cloud Server:** `https://medical-agent-server.fastmcp.app/mcp`

## ✨ **Features**

- 🧠 **AI-Powered Analysis**: Claude Sonnet 4 + GPT-4o fallback
- 💳 **Stripe Payment Integration**: Live billing with multiple tiers
- 🔒 **HIPAA-Compliant Processing**: Secure medical data handling
- 📊 **Multi-Tier Analysis**: Basic ($0.10), Comprehensive ($0.50), Batch ($0.05)
- 🌐 **Cross-Platform Integration**: Claude Desktop, Cursor IDE, Gemini CLI compatible
- ⚡ **FastMCP Cloud**: Enterprise-grade deployment and scaling

## 🤖 **AI Models**

- **Primary**: Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- **Fallback**: OpenAI GPT-4o (`gpt-4o`)
- **Analysis Types**: Basic extraction, comprehensive insights, batch processing
- **Token Tracking**: Real-time usage monitoring for accurate billing

## 📋 **Available Tools**

### 🏥 **Medical Analysis**
- `analyze_medical_document` - AI-powered document analysis using latest LLM models
- `get_patient_summary` - Retrieve structured patient information
- `get_available_services` - Service catalog with pricing and features

### 💰 **Billing & Payment**
- `calculate_billing` - Multi-tier pricing with volume discounts
- `create_customer` - Stripe customer management
- `create_payment_intent` - Secure payment processing
- `confirm_payment` - Payment verification and status
- `process_paid_analysis` - Complete end-to-end paid workflow
- `get_customer_info` - Customer billing history and details

### 🔧 **System**
- `health_check` - Server monitoring and API status validation

## 🔗 **Integration**

### Claude Desktop
```bash
claude mcp add --scope local --transport http Medical-agent-server https://medical-agent-server.fastmcp.app/mcp
```

### Claude Code
```bash
claude mcp add Medical-agent-server https://medical-agent-server.fastmcp.app/mcp
```

### Cursor IDE
```json
{
  "servers": {
    "medical-agent": {
      "command": "mcp",
      "args": ["--transport", "http", "https://medical-agent-server.fastmcp.app/mcp"]
    }
  }
}
```

## 🏗️ **Local Development**

### Prerequisites
- Python 3.12+
- Virtual environment
- API keys for Anthropic and/or OpenAI

### Setup
```bash
# Clone repository
git clone https://github.com/[username]/medical-agent-fastmcp
cd medical-agent-fastmcp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.template .env
# Edit .env with your API keys
```

### Environment Variables
```bash
ANTHROPIC_API_KEY=sk-ant-api03-your_key_here
OPENAI_API_KEY=sk-proj-your_key_here
STRIPE_API_KEY=sk_live_your_key_here
```

### Testing
```bash
# Test AI functionality
python3 test_medical_server.py

# Test OpenAI fallback
python3 test_openai_fallback.py

# Import verification
python3 -c "from medical_mcp_server import mcp; print('✅ Server ready')"
```

## 💊 **Usage Examples**

### Medical Document Analysis
```python
# Basic analysis - $0.10
analyze_medical_document(
    document_content="SOAP NOTE: Patient presents with chest pain...",
    analysis_type="basic",
    patient_id="patient_001"
)

# Comprehensive analysis - $0.50
analyze_medical_document(
    document_content="Complex medical case with multiple conditions...",
    analysis_type="comprehensive",
    patient_id="patient_002"
)
```

### Payment Processing
```python
# Create customer
customer = create_customer(
    email="dr.smith@clinic.com",
    name="Dr. Jennifer Smith"
)

# Process payment
payment = create_payment_intent(
    customer_id=customer["customer_id"],
    analysis_type="comprehensive",
    document_count=1
)
```

## 📊 **Billing Tiers**

| Tier | Price | Description | Features |
|------|-------|-------------|----------|
| **Basic** | $0.10 | Essential analysis | Vital signs, medications, conditions |
| **Comprehensive** | $0.50 | Full clinical insights | Risk assessment, recommendations, follow-up |
| **Batch** | $0.05 | Volume processing | Bulk analysis with enterprise discounts |

**Volume Discounts:**
- 10+ documents: 10% discount
- Enterprise customers: Additional 15% discount

## 🔧 **Technical Specifications**

- **Framework**: FastMCP 2.2.6+
- **Language**: Python 3.12
- **Deployment**: FastMCP Cloud
- **Payment Processing**: Stripe Live API
- **AI Providers**: Anthropic API, OpenAI API
- **Protocol**: Model Context Protocol (MCP)

## 📈 **Performance**

- **Response Time**: < 2 seconds for document analysis
- **Availability**: 99.9% uptime SLA via FastMCP Cloud
- **Scalability**: Auto-scaling based on request volume
- **Token Efficiency**: Optimized prompts for cost-effective analysis

## 🛡️ **Security & Compliance**

- **HIPAA Compliant**: Secure medical data processing
- **PHI Protection**: No data persistence or logging of medical content
- **API Security**: TLS encryption for all communications
- **Payment Security**: PCI DSS compliant via Stripe

## 📚 **Documentation**

- **API Reference**: Available through FastMCP Cloud dashboard
- **Integration Guide**: See `CLAUDE.md` for detailed setup
- **Development Story**: Read our [Medium article](link) for implementation details

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 **Links**

- **Live Server**: https://medical-agent-server.fastmcp.app/mcp
- **FastMCP Cloud**: https://fastmcp.app
- **Model Context Protocol**: https://modelcontextprotocol.io
- **Claude Desktop**: https://claude.ai/desktop
- **Cursor IDE**: https://cursor.sh

## 📞 **Support**

For issues, questions, or feature requests:
- Create an issue on GitHub
- Check server health: `https://medical-agent-server.fastmcp.app/health`
- Review FastMCP Cloud logs for deployment issues

---

*Built with ❤️ for healthcare professionals using Claude Sonnet 4 and FastMCP Cloud*