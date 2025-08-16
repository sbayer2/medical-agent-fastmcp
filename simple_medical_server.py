from fastmcp import FastMCP

# Create FastMCP server instance
mcp = FastMCP("MedicalAgent")

@mcp.tool()
def health_check() -> str:
    """Health check for the medical server."""
    return "Medical Agent MCP Server is healthy and running!"

@mcp.tool()
def analyze_medical_document(document_content: str) -> dict:
    """Analyze a medical document and extract basic information."""
    
    # Simple analysis
    content_lower = document_content.lower()
    
    # Extract basic information
    findings = {
        "timestamp": "2025-08-16T04:00:00Z",
        "document_analyzed": True,
        "vital_signs_detected": any(term in content_lower for term in ["bp", "blood pressure", "hr", "heart rate", "temp"]),
        "medications_detected": any(med in content_lower for med in ["lisinopril", "metformin", "aspirin"]),
        "conditions_detected": any(condition in content_lower for condition in ["diabetes", "hypertension", "asthma"]),
        "analysis_summary": f"Document contains {len(document_content)} characters"
    }
    
    return findings

@mcp.tool()
def calculate_billing(analysis_type: str = "basic") -> dict:
    """Calculate billing for medical analysis."""
    
    prices = {
        "basic": 0.10,
        "comprehensive": 0.50,
        "batch": 0.05
    }
    
    price = prices.get(analysis_type, 0.10)
    
    return {
        "analysis_type": analysis_type,
        "price": price,
        "currency": "USD",
        "billing_date": "2025-08-16T04:00:00Z"
    }