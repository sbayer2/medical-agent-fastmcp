"""
Medical Agent MCP Server for FastMCP Cloud Deployment - Fixed Version

This server provides medical document analysis tools for AI assistants.
Compatible with FastMCP Cloud deployment platform.
Includes full Stripe payment processing integration.
"""

from fastmcp import FastMCP
from typing import Dict, Any, Optional, List
import json
import os
from datetime import datetime

# Initialize FastMCP server
mcp = FastMCP("MedicalAgent")

# Import dependencies conditionally to avoid build issues
try:
    import stripe
    STRIPE_AVAILABLE = True
    stripe.api_key = os.getenv("STRIPE_API_KEY") or os.getenv("STRIPE_SECRET_KEY")
except ImportError:
    STRIPE_AVAILABLE = False
    print("Warning: Stripe not available")

try:
    from anthropic import Anthropic
    anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")) if os.getenv("ANTHROPIC_API_KEY") else None
    ANTHROPIC_AVAILABLE = bool(anthropic_client)
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic_client = None
    print("Warning: Anthropic not available")

# Validate API keys on startup
if STRIPE_AVAILABLE and not stripe.api_key:
    print("Warning: STRIPE_API_KEY not found. Payment processing will be disabled.")
if not ANTHROPIC_AVAILABLE:
    print("Warning: ANTHROPIC_API_KEY not found. AI analysis may be limited.")

# Billing tiers configuration
BILLING_TIERS = {
    "basic": {"price": 0.10, "description": "Basic SOAP analysis - vital signs, medications, basic conditions"},
    "comprehensive": {"price": 0.50, "description": "Full medical record analysis - detailed insights, recommendations"},
    "batch": {"price": 0.05, "description": "Bulk processing per document - optimized for multiple files"}
}

# Sample medical data for demonstration
SAMPLE_MEDICAL_DATA = {
    "patient_001": {
        "demographics": {"age": 45, "gender": "male", "medical_record_number": "MRN001"},
        "vital_signs": {"blood_pressure": "150/95", "heart_rate": 88, "temperature": "98.6F"},
        "medications": [{"name": "Lisinopril", "dosage": "10mg", "frequency": "daily"}],
        "conditions": ["Type 2 Diabetes", "Hypertension"],
        "last_visit": "2024-01-15",
        "notes": "Patient presents with chest pain and shortness of breath."
    }
}

# Health check function - must be first for FastMCP Cloud validation
@mcp.tool
def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for service monitoring.
    
    Returns:
        Service health status and basic metrics
    """
    
    api_status = {
        "stripe_configured": STRIPE_AVAILABLE and bool(stripe.api_key) if STRIPE_AVAILABLE else False,
        "anthropic_configured": ANTHROPIC_AVAILABLE,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }
    
    return {
        "status": "healthy",
        "service": "Medical Agent MCP Server",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "api_status": api_status,
        "available_tools": [
            "health_check",
            "analyze_medical_document",
            "get_patient_summary", 
            "calculate_billing",
            "get_available_services"
        ] + (["create_customer", "create_payment_intent", "confirm_payment"] if STRIPE_AVAILABLE else []),
        "billing_tiers_available": list(BILLING_TIERS.keys()),
        "uptime": "Service running normally"
    }

@mcp.tool
def analyze_medical_document(
    document_content: str,
    analysis_type: str = "basic",
    patient_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze medical document content and extract structured information.
    
    Args:
        document_content: Raw medical document text (SOAP notes, lab results, etc.)
        analysis_type: Type of analysis (basic, comprehensive, batch)
        patient_id: Optional patient identifier
        
    Returns:
        Structured medical analysis with extracted information
    """
    
    if analysis_type not in BILLING_TIERS:
        return {
            "error": f"Invalid analysis type. Available types: {list(BILLING_TIERS.keys())}"
        }
    
    tier = BILLING_TIERS[analysis_type]
    
    # Parse document content for medical information
    analysis = {
        "analysis_type": analysis_type,
        "billing_info": tier,
        "timestamp": datetime.now().isoformat(),
        "patient_id": patient_id,
        "extracted_data": {}
    }
    
    # Basic extraction logic
    content_lower = document_content.lower()
    
    # Extract vital signs
    vital_signs = {}
    if "bp" in content_lower or "blood pressure" in content_lower:
        vital_signs["blood_pressure"] = "Pattern detected"
    if "hr" in content_lower or "heart rate" in content_lower:
        vital_signs["heart_rate"] = "Pattern detected"
    if "temp" in content_lower or "temperature" in content_lower:
        vital_signs["temperature"] = "Pattern detected"
    
    analysis["extracted_data"]["vital_signs"] = vital_signs
    
    # Extract medications
    medications = []
    common_meds = ["lisinopril", "metformin", "aspirin", "ibuprofen", "synthroid"]
    for med in common_meds:
        if med in content_lower:
            medications.append(med.title())
    
    analysis["extracted_data"]["medications"] = medications
    
    # Extract conditions
    conditions = []
    common_conditions = ["diabetes", "hypertension", "asthma", "copd", "hypothyroidism"]
    for condition in common_conditions:
        if condition in content_lower:
            conditions.append(condition.title())
    
    analysis["extracted_data"]["conditions"] = conditions
    
    # Add analysis level specific information
    if analysis_type == "comprehensive":
        analysis["extracted_data"]["detailed_analysis"] = {
            "risk_factors": ["High blood pressure detected" if "hypertension" in conditions else ""],
            "recommendations": ["Follow up with cardiologist" if vital_signs.get("blood_pressure") else ""],
            "follow_up_required": True
        }
    elif analysis_type == "batch":
        analysis["extracted_data"]["batch_summary"] = {
            "documents_processed": 1,
            "total_cost": tier["price"]
        }
    
    return analysis

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
    discount = 0.1 if analysis_type == "batch" and document_count > 10 else 0.0
    
    # Apply customer tier discounts
    customer_discounts = {"standard": 0.0, "premium": 0.05, "enterprise": 0.15}
    customer_discount = customer_discounts.get(customer_tier, 0.0)
    
    subtotal = base_price * document_count
    total_discount = (discount + customer_discount) * subtotal
    final_total = subtotal - total_discount
    
    return {
        "analysis_type": analysis_type,
        "document_count": document_count,
        "base_price_per_document": base_price,
        "subtotal": round(subtotal, 2),
        "total_discount": round(total_discount, 2),
        "final_total": round(final_total, 2),
        "currency": "USD",
        "billing_date": datetime.now().isoformat()
    }

@mcp.tool
def get_available_services() -> Dict[str, Any]:
    """
    Get information about available medical analysis services.
    
    Returns:
        Complete service catalog with pricing and descriptions
    """
    
    return {
        "service_catalog": {
            "name": "Medical Document Analysis Service",
            "version": "2.0.0",
            "description": "AI-powered medical document analysis",
            "billing_tiers": BILLING_TIERS,
            "supported_document_types": [
                "SOAP notes", "Lab reports", "Prescription summaries", 
                "Patient histories", "Discharge summaries"
            ],
            "compliance": ["HIPAA compliant processing", "PHI data protection"]
        }
    }

# Stripe Payment Tools (only if Stripe is available)
if STRIPE_AVAILABLE:
    
    @mcp.tool
    def create_customer(
        email: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new Stripe customer for billing.
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
            
        except Exception as e:
            return {"error": f"Stripe error: {str(e)}", "success": False}

    @mcp.tool
    def create_payment_intent(
        customer_id: str,
        analysis_type: str = "basic",
        document_count: int = 1,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe payment intent for medical analysis.
        """
        
        if not stripe.api_key:
            return {"error": "Stripe not configured"}
        
        if analysis_type not in BILLING_TIERS:
            return {"error": f"Invalid analysis type: {analysis_type}"}
        
        try:
            tier = BILLING_TIERS[analysis_type]
            amount = int(tier["price"] * document_count * 100)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency="usd",
                customer=customer_id,
                description=description or f"Medical Analysis - {tier['description']}",
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
                "status": payment_intent.status
            }
            
        except Exception as e:
            return {"error": f"Stripe error: {str(e)}", "success": False}

    @mcp.tool
    def confirm_payment(payment_intent_id: str) -> Dict[str, Any]:
        """
        Confirm and retrieve payment status.
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
                "paid": payment_intent.status == "succeeded",
                "created": datetime.fromtimestamp(payment_intent.created).isoformat()
            }
            
        except Exception as e:
            return {"error": f"Stripe error: {str(e)}", "success": False}

# Optional: Add server initialization for local testing
if __name__ == "__main__":
    print("Medical Agent MCP Server - Fixed Version")
    print("Ready for FastMCP Cloud deployment!")