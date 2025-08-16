# Medical Agent FastMCP Server

AI-powered medical document analysis with Stripe payment integration for FastMCP Cloud.

## 🏥 Features

- **Medical Document Analysis** with 3 billing tiers
- **Full Stripe Payment Integration** 
- **Patient Data Management**
- **10 Available Tools** for comprehensive medical analysis
- **Health Monitoring & API Status Checks**

## 🚀 Quick Deploy to FastMCP Cloud

1. **Select this repository** in FastMCP Cloud
2. **Configure entrypoint**: `medical_mcp_server.py:mcp`
3. **Add environment variables**:
   - `STRIPE_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `OPENAI_API_KEY` (optional)
4. **Deploy** automatically to your unique URL

## 💰 Billing Tiers

- **Basic** ($0.10): Vital signs, medications, basic conditions
- **Comprehensive** ($0.50): Full analysis with insights & recommendations  
- **Batch** ($0.05): Bulk processing with volume discounts

## 🛠️ Available Tools

### Payment Tools
- `create_customer` - Create Stripe customers
- `create_payment_intent` - Set up payments
- `confirm_payment` - Verify payment status
- `process_paid_analysis` - Execute analysis after payment
- `get_customer_info` - Retrieve customer data

### Medical Analysis Tools
- `analyze_medical_document` - Core medical analysis
- `get_patient_summary` - Patient data retrieval
- `calculate_billing` - Cost calculations
- `get_available_services` - Service catalog
- `health_check` - System monitoring

## 📝 Usage Example

```python
# Payment workflow
create_customer(email="doctor@hospital.com", name="Dr. Smith")
create_payment_intent(customer_id="cus_xxx", analysis_type="comprehensive")
process_paid_analysis(payment_intent_id="pi_xxx", document_content="Patient data...")

# Direct analysis
analyze_medical_document("BP 150/95, HR 88, Diabetes", "basic")
```

## 🔒 Security

- HIPAA compliant processing
- Environment variable configuration
- Stripe payment security
- Authentication recommended

---

**Ready for FastMCP Cloud deployment!** 🚀

Generated with [Claude Code](https://claude.ai/code)