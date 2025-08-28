"""
Medical Agent MCP Server for FastMCP Cloud Deployment

This server provides medical document analysis tools for AI assistants.
Compatible with FastMCP Cloud deployment platform.
Includes full Stripe payment processing integration.
"""

from fastmcp import FastMCP
from typing import Dict, Any, Optional, List
import json
import os
from datetime import datetime
import asyncio
import stripe
import httpx
from anthropic import Anthropic
from openai import AsyncOpenAI

# Initialize FastMCP server
mcp = FastMCP("MedicalAgent")

# Initialize API clients
stripe.api_key = os.getenv("STRIPE_API_KEY") or os.getenv("STRIPE_SECRET_KEY")
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")) if os.getenv("ANTHROPIC_API_KEY") else None
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None

# Validate API keys on startup
if not stripe.api_key:
    print("Warning: STRIPE_API_KEY not found. Payment processing will be disabled.")
if not anthropic_client:
    print("Warning: ANTHROPIC_API_KEY not found. Primary AI analysis will use fallback.")
if not openai_client:
    print("Warning: OPENAI_API_KEY not found. Fallback AI analysis not available.")

# Billing tiers configuration
BILLING_TIERS = {
    "basic": {"price": 0.10, "description": "Basic SOAP analysis - vital signs, medications, basic conditions"},
    "comprehensive": {"price": 0.50, "description": "Full medical record analysis - detailed insights, recommendations"},
    "batch": {"price": 0.05, "description": "Bulk processing per document - optimized for multiple files"},
    "complicated": {"price": 0.75, "description": "Multi-step clinical reasoning with quality assurance and specialist-level analysis"}
}

# Sample medical data for demonstration (in production, this would connect to actual medical databases)
SAMPLE_MEDICAL_DATA = {
    "patient_001": {
        "demographics": {
            "age": 45,
            "gender": "male",
            "medical_record_number": "MRN001"
        },
        "vital_signs": {
            "blood_pressure": "150/95",
            "heart_rate": 88,
            "temperature": "98.6F",
            "respiratory_rate": 16,
            "oxygen_saturation": "98%"
        },
        "medications": [
            {"name": "Lisinopril", "dosage": "10mg", "frequency": "daily"},
            {"name": "Metformin", "dosage": "500mg", "frequency": "BID"}
        ],
        "conditions": ["Type 2 Diabetes", "Hypertension"],
        "last_visit": "2024-01-15",
        "notes": "Patient presents with chest pain and shortness of breath. Stable vital signs."
    },
    "patient_002": {
        "demographics": {
            "age": 32,
            "gender": "female",
            "medical_record_number": "MRN002"
        },
        "vital_signs": {
            "blood_pressure": "120/80",
            "heart_rate": 72,
            "temperature": "98.2F",
            "respiratory_rate": 14,
            "oxygen_saturation": "99%"
        },
        "medications": [
            {"name": "Synthroid", "dosage": "75mcg", "frequency": "daily"}
        ],
        "conditions": ["Hypothyroidism"],
        "last_visit": "2024-01-10",
        "notes": "Regular follow-up for thyroid management. Patient doing well."
    }
}

# Stripe Payment Tools

@mcp.tool
def create_customer(
    email: str,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new Stripe customer for billing.
    
    Args:
        email: Customer email address
        name: Customer name
        description: Optional customer description
        
    Returns:
        Customer creation result with customer ID
    """
    
    if not stripe.api_key:
        return {"error": "Stripe not configured"}
    
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name,
            description=description or f"Medical Analysis Customer - {email}"
        )
        
        return {
            "success": True,
            "customer_id": customer.id,
            "email": customer.email,
            "created": datetime.fromtimestamp(customer.created).isoformat()
        }
        
    except stripe.error.StripeError as e:
        return {
            "error": f"Stripe error: {str(e)}",
            "success": False
        }

@mcp.tool
def create_payment_intent(
    customer_id: str,
    analysis_type: str = "basic",
    document_count: int = 1,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a Stripe payment intent for medical analysis.
    
    Args:
        customer_id: Stripe customer ID
        analysis_type: Type of analysis (basic, comprehensive, batch)
        document_count: Number of documents to analyze
        description: Optional payment description
        
    Returns:
        Payment intent with client secret for frontend payment
    """
    
    if not stripe.api_key:
        return {"error": "Stripe not configured"}
    
    if analysis_type not in BILLING_TIERS:
        return {"error": f"Invalid analysis type: {analysis_type}"}
    
    try:
        tier = BILLING_TIERS[analysis_type]
        amount = int(tier["price"] * document_count * 100)  # Convert to cents
        
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            customer=customer_id,
            description=description or f"Medical Analysis - {tier['description']} x{document_count}",
            metadata={
                "analysis_type": analysis_type,
                "document_count": str(document_count),
                "service": "medical_analysis"
            }
        )
        
        return {
            "success": True,
            "payment_intent_id": payment_intent.id,
            "client_secret": payment_intent.client_secret,
            "amount": amount,
            "currency": payment_intent.currency,
            "status": payment_intent.status,
            "analysis_type": analysis_type,
            "document_count": document_count
        }
        
    except stripe.error.StripeError as e:
        return {
            "error": f"Stripe error: {str(e)}",
            "success": False
        }

@mcp.tool
def confirm_payment(payment_intent_id: str) -> Dict[str, Any]:
    """
    Confirm and retrieve payment status.
    
    Args:
        payment_intent_id: Stripe payment intent ID
        
    Returns:
        Payment confirmation and metadata
    """
    
    if not stripe.api_key:
        return {"error": "Stripe not configured"}
    
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        return {
            "success": True,
            "payment_intent_id": payment_intent.id,
            "status": payment_intent.status,
            "amount_received": payment_intent.amount_received,
            "currency": payment_intent.currency,
            "customer_id": payment_intent.customer,
            "metadata": payment_intent.metadata,
            "paid": payment_intent.status == "succeeded",
            "created": datetime.fromtimestamp(payment_intent.created).isoformat()
        }
        
    except stripe.error.StripeError as e:
        return {
            "error": f"Stripe error: {str(e)}",
            "success": False
        }

@mcp.tool
async def process_paid_analysis(
    payment_intent_id: str,
    document_content: str,
    patient_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process medical analysis after payment confirmation.
    
    Args:
        payment_intent_id: Confirmed Stripe payment intent ID
        document_content: Medical document text to analyze
        patient_id: Optional patient identifier
        
    Returns:
        Medical analysis results with payment confirmation
    """
    
    # First confirm payment
    payment_result = confirm_payment(payment_intent_id)
    
    if not payment_result.get("success") or not payment_result.get("paid"):
        return {
            "error": "Payment not confirmed or failed",
            "payment_status": payment_result
        }
    
    # Extract analysis parameters from payment metadata
    metadata = payment_result.get("metadata", {})
    analysis_type = metadata.get("analysis_type", "basic")
    
    # Perform the medical analysis with AI
    analysis_result = await analyze_medical_document(
        document_content=document_content,
        analysis_type=analysis_type,
        patient_id=patient_id
    )
    
    # Add payment confirmation to result
    analysis_result.update({
        "payment_confirmed": True,
        "payment_intent_id": payment_intent_id,
        "amount_paid": payment_result.get("amount_received", 0) / 100,  # Convert from cents
        "currency": payment_result.get("currency"),
        "processed_at": datetime.now().isoformat()
    })
    
    return analysis_result

@mcp.tool
def get_customer_info(customer_id: str) -> Dict[str, Any]:
    """
    Retrieve Stripe customer information.
    
    Args:
        customer_id: Stripe customer ID
        
    Returns:
        Customer information and payment history
    """
    
    if not stripe.api_key:
        return {"error": "Stripe not configured"}
    
    try:
        customer = stripe.Customer.retrieve(customer_id)
        
        # Get recent payment intents
        payment_intents = stripe.PaymentIntent.list(
            customer=customer_id,
            limit=10
        )
        
        return {
            "success": True,
            "customer_id": customer.id,
            "email": customer.email,
            "name": customer.name,
            "description": customer.description,
            "created": datetime.fromtimestamp(customer.created).isoformat(),
            "recent_payments": [
                {
                    "id": pi.id,
                    "amount": pi.amount,
                    "currency": pi.currency,
                    "status": pi.status,
                    "created": datetime.fromtimestamp(pi.created).isoformat(),
                    "metadata": pi.metadata
                }
                for pi in payment_intents.data
            ]
        }
        
    except stripe.error.StripeError as e:
        return {
            "error": f"Stripe error: {str(e)}",
            "success": False
        }

@mcp.tool
async def analyze_medical_document(
    document_content: str,
    analysis_type: str = "basic",
    patient_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze medical document content using Claude Sonnet 4 AI.
    
    Args:
        document_content: Raw medical document text (SOAP notes, lab results, etc.)
        analysis_type: Type of analysis (basic, comprehensive, batch)
        patient_id: Optional patient identifier
        
    Returns:
        AI-powered structured medical analysis with extracted information
    """
    
    if analysis_type not in BILLING_TIERS:
        return {
            "error": f"Invalid analysis type. Available types: {list(BILLING_TIERS.keys())}"
        }
    
    # Enhanced error diagnostics
    if not anthropic_client and not openai_client:
        import os
        anthropic_key_present = bool(os.getenv('ANTHROPIC_API_KEY'))
        openai_key_present = bool(os.getenv('OPENAI_API_KEY'))
        return {
            "error": "No AI providers configured",
            "debug_info": {
                "anthropic_key_detected": anthropic_key_present,
                "openai_key_detected": openai_key_present,
                "anthropic_client_status": str(type(anthropic_client)) if anthropic_client else "None",
                "openai_client_status": str(type(openai_client)) if openai_client else "None",
                "environment": "lambda" if os.getenv('AWS_LAMBDA_FUNCTION_NAME') else "local"
            }
        }
    
    tier = BILLING_TIERS[analysis_type]
    
    # Define system prompts based on analysis type
    if analysis_type == "basic":
        system_prompt = """You are a medical AI assistant specializing in basic medical document analysis.
        
Analyze the provided medical document and extract:
        1. **Vital Signs**: Blood pressure, heart rate, temperature, respiratory rate, oxygen saturation
        2. **Medications**: Names, dosages, frequencies
        3. **Medical Conditions**: Diagnoses, conditions, symptoms
        4. **Basic Assessment**: Primary concerns and chief complaints
        
Provide your analysis in a structured JSON format with clear categories.
        Focus on accuracy and completeness of basic medical information extraction."""
        
    elif analysis_type == "comprehensive":
        system_prompt = """You are an expert medical AI assistant providing comprehensive clinical analysis.
        
Perform a thorough analysis of the medical document including:
        1. **Complete Data Extraction**: All vital signs, medications, conditions, lab results
        2. **Clinical Assessment**: Chief complaint, history of present illness, risk factors
        3. **Treatment Analysis**: Current medications, dosages, treatment plans
        4. **Risk Stratification**: Identify potential complications and risk factors
        5. **Clinical Recommendations**: Evidence-based suggestions for care optimization
        6. **Follow-up Requirements**: Necessary monitoring, tests, or specialist referrals
        7. **Quality Assessment**: Data completeness, critical values, urgent findings
        
Provide detailed clinical insights with medical reasoning and recommendations.
        Use structured JSON format with comprehensive categories."""
        
    elif analysis_type == "complicated":
        system_prompt = """You are a specialist medical AI performing advanced clinical analysis.

WORKFLOW (5 Steps):
1. VALIDATE: Document type, completeness score (1-10), missing data
2. EXTRACT: Vitals, medications, conditions, labs, procedures with context
3. ANALYZE: Chief complaint, differentials, risk stratification, comorbidities
4. VERIFY: Critical values, drug interactions, guideline adherence
5. RECOMMEND: Immediate actions, follow-up, monitoring, referrals

OUTPUT: JSON with sections: document_assessment, clinical_data, reasoning_analysis, quality_assurance, recommendations, metadata.

Focus on clinical accuracy and actionable insights."""
        
    else:  # batch
        system_prompt = """You are a medical AI assistant optimized for efficient batch processing.
        
Extract key medical information efficiently:
        1. **Essential Data**: Vital signs, medications, primary conditions
        2. **Critical Flags**: Urgent findings requiring immediate attention
        3. **Summary Statistics**: Document type, completeness score
        4. **Batch Metrics**: Processing efficiency and quality indicators
        
Provide concise but complete analysis suitable for high-volume processing.
        Use structured JSON format optimized for batch operations."""
    
    try:
        # Try Claude Sonnet 4 first, fallback to OpenAI GPT-4
        if anthropic_client:
            # Add timeout handling for API calls
            import time
            start_time = time.time()
            
            message = anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10000 if analysis_type in ["complicated", "comprehensive"] else 1000,
                temperature=0.1,  # Low temperature for medical accuracy
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Please analyze the following medical document and provide a structured analysis:

=== MEDICAL DOCUMENT ===
{document_content}
=== END DOCUMENT ===

Provide your analysis in JSON format with appropriate medical categories and extracted information."""
                    }
                ],
                timeout=None if analysis_type in ["complicated", "comprehensive"] else 45.0  # No timeout for complex analysis
            )
            
            processing_time = time.time() - start_time
            ai_analysis = message.content[0].text
            model_used = "claude-sonnet-4-20250514"
            tokens_used = {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
                "total_tokens": message.usage.input_tokens + message.usage.output_tokens
            }
        elif openai_client:
            # Fallback to OpenAI GPT-4
            completion = await openai_client.chat.completions.create(
                model="gpt-4o",
                max_tokens=10000 if analysis_type in ["complicated", "comprehensive"] else 1000,
                temperature=0.1,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"""Please analyze the following medical document and provide a structured analysis:

=== MEDICAL DOCUMENT ===
{document_content}
=== END DOCUMENT ===

Provide your analysis in JSON format with appropriate medical categories and extracted information."""
                    }
                ]
            )
            ai_analysis = completion.choices[0].message.content
            model_used = "gpt-4o"
            tokens_used = {
                "input_tokens": completion.usage.prompt_tokens,
                "output_tokens": completion.usage.completion_tokens,
                "total_tokens": completion.usage.total_tokens
            }
        
        # Construct response with AI analysis
        analysis = {
            "analysis_type": analysis_type,
            "billing_info": tier,
            "timestamp": datetime.now().isoformat(),
            "patient_id": patient_id,
            "model_used": model_used,
            "ai_analysis": ai_analysis,
            "tokens_used": tokens_used,
            "processing_time_seconds": round(processing_time, 2) if 'processing_time' in locals() else None
        }
        
        # Add analysis-specific metadata
        if analysis_type == "comprehensive":
            analysis["analysis_features"] = [
                "Complete data extraction",
                "Clinical assessment", 
                "Risk stratification",
                "Treatment recommendations",
                "Follow-up planning"
            ]
        elif analysis_type == "complicated":
            analysis["analysis_features"] = [
                "Multi-step clinical reasoning",
                "Specialist-level analysis",
                "Quality assurance validation",
                "Evidence-based recommendations",
                "Clinical decision support",
                "Risk stratification",
                "Medication interaction analysis",
                "Guideline adherence assessment"
            ]
        elif analysis_type == "batch":
            analysis["batch_info"] = {
                "documents_processed": 1,
                "processing_cost": tier["price"],
                "efficiency_optimized": True
            }
        
        return analysis
        
    except Exception as e:
        import os
        error_type = type(e).__name__
        error_details = {
            "error": f"AI analysis failed: {str(e)}",
            "error_type": error_type,
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat(),
            "environment": "lambda" if os.getenv('AWS_LAMBDA_FUNCTION_NAME') else "local",
            "anthropic_available": bool(anthropic_client),
            "openai_available": bool(openai_client)
        }
        
        # Specific error handling
        if "timeout" in str(e).lower() or "timed out" in str(e).lower():
            error_details["fix_suggestion"] = "API timeout - consider using 'basic' or 'comprehensive' analysis for faster processing"
        elif "rate limit" in str(e).lower() or "429" in str(e):
            error_details["fix_suggestion"] = "Rate limit exceeded - please try again in a few moments"
        elif "authentication" in str(e).lower() or "401" in str(e):
            error_details["fix_suggestion"] = "API authentication failed - check environment variables"
        
        return error_details

@mcp.tool
def get_patient_summary(patient_id: str) -> Dict[str, Any]:
    """
    Retrieve patient summary information.
    
    Args:
        patient_id: Patient identifier
        
    Returns:
        Patient summary with demographics, conditions, and recent activity
    """
    
    if patient_id not in SAMPLE_MEDICAL_DATA:
        return {
            "error": f"Patient {patient_id} not found",
            "available_patients": list(SAMPLE_MEDICAL_DATA.keys())
        }
    
    patient_data = SAMPLE_MEDICAL_DATA[patient_id]
    
    summary = {
        "patient_id": patient_id,
        "summary_generated": datetime.now().isoformat(),
        "demographics": patient_data["demographics"],
        "current_conditions": patient_data["conditions"],
        "active_medications": len(patient_data["medications"]),
        "last_visit": patient_data["last_visit"],
        "vital_signs_last_recorded": patient_data["vital_signs"]
    }
    
    return summary

@mcp.tool
def calculate_billing(
    analysis_type: str,
    document_count: int = 1,
    customer_tier: str = "standard"
) -> Dict[str, Any]:
    """
    Calculate billing for medical analysis services.
    
    Args:
        analysis_type: Type of analysis (basic, comprehensive, batch)
        document_count: Number of documents to process
        customer_tier: Customer tier for potential discounts
        
    Returns:
        Billing calculation with itemized costs
    """
    
    if analysis_type not in BILLING_TIERS:
        return {
            "error": f"Invalid analysis type. Available types: {list(BILLING_TIERS.keys())}"
        }
    
    tier = BILLING_TIERS[analysis_type]
    base_price = tier["price"]
    
    # Apply volume discounts for batch processing
    if analysis_type == "batch" and document_count > 10:
        discount = 0.1  # 10% discount for bulk
    else:
        discount = 0.0
    
    # Apply customer tier discounts
    customer_discounts = {
        "standard": 0.0,
        "premium": 0.05,
        "enterprise": 0.15
    }
    
    customer_discount = customer_discounts.get(customer_tier, 0.0)
    
    subtotal = base_price * document_count
    total_discount = (discount + customer_discount) * subtotal
    final_total = subtotal - total_discount
    
    billing = {
        "analysis_type": analysis_type,
        "document_count": document_count,
        "base_price_per_document": base_price,
        "subtotal": round(subtotal, 2),
        "volume_discount": round(discount * subtotal, 2),
        "customer_tier_discount": round(customer_discount * subtotal, 2),
        "total_discount": round(total_discount, 2),
        "final_total": round(final_total, 2),
        "currency": "USD",
        "billing_date": datetime.now().isoformat()
    }
    
    return billing

@mcp.tool
def get_available_services() -> Dict[str, Any]:
    """
    Get information about available medical analysis services.
    
    Returns:
        Complete service catalog with pricing and descriptions
    """
    
    services = {
        "service_catalog": {
            "name": "Medical Document Analysis Service",
            "version": "1.0.0",
            "description": "AI-powered medical document analysis and information extraction",
            "billing_tiers": BILLING_TIERS,
            "features": {
                "basic": [
                    "Vital signs extraction",
                    "Medication identification",
                    "Basic condition recognition",
                    "SOAP note parsing"
                ],
                "comprehensive": [
                    "All basic features",
                    "Detailed clinical insights",
                    "Risk factor analysis",
                    "Treatment recommendations",
                    "Follow-up scheduling suggestions"
                ],
                "batch": [
                    "Bulk document processing",
                    "Volume discounts",
                    "Batch reporting",
                    "API integration support"
                ]
            },
            "supported_document_types": [
                "SOAP notes",
                "Lab reports",
                "Prescription summaries",
                "Patient histories",
                "Discharge summaries"
            ],
            "compliance": [
                "HIPAA compliant processing",
                "PHI data protection",
                "Audit trail logging"
            ]
        },
        "sample_usage": {
            "analyze_document": "analyze_medical_document('Patient presents with...', 'comprehensive')",
            "get_patient_info": "get_patient_summary('patient_001')",
            "calculate_costs": "calculate_billing('basic', 5, 'premium')"
        }
    }
    
    return services

@mcp.tool
def simulate_payment_success(payment_intent_id: str) -> Dict[str, Any]:
    """
    Simulate successful payment for testing purposes.
    
    Args:
        payment_intent_id: Stripe payment intent ID to simulate success for
        
    Returns:
        Simulated payment success response
    """
    
    # This is for testing only - simulates payment success
    return {
        "success": True,
        "payment_intent_id": payment_intent_id,
        "status": "succeeded",
        "amount_received": "simulated",
        "simulation": True,
        "message": "Payment simulated as successful for testing purposes",
        "timestamp": datetime.now().isoformat()
    }

# Health check function for monitoring
@mcp.tool
def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for service monitoring.
    
    Returns:
        Service health status and basic metrics
    """
    
    # Check API keys status
    api_status = {
        "stripe_configured": bool(stripe.api_key),
        "anthropic_configured": bool(anthropic_client),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }
    
    return {
        "status": "healthy",
        "service": "Medical Agent MCP Server with Stripe Integration",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "api_status": api_status,
        "available_tools": [
            "analyze_medical_document",
            "get_patient_summary", 
            "calculate_billing",
            "get_available_services",
            "health_check",
            "create_customer",
            "create_payment_intent",
            "confirm_payment",
            "process_paid_analysis",
            "get_customer_info"
        ],
        "payment_tools": [
            "create_customer",
            "create_payment_intent", 
            "confirm_payment",
            "process_paid_analysis",
            "get_customer_info"
        ],
        "billing_tiers_available": list(BILLING_TIERS.keys()),
        "uptime": "Service running normally"
    }

# Optional: Add server initialization for local testing
if __name__ == "__main__":
    print("Medical Agent MCP Server")
    print("Available tools:")
    for tool_name in ["analyze_medical_document", "get_patient_summary", "calculate_billing", "get_available_services", "health_check"]:
        print(f"  - {tool_name}")
    print("\nReady for FastMCP Cloud deployment!")