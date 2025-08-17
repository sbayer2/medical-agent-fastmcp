"""
Simplified Medical Agent - Without Stage Fright!
This version runs without the full MCP server orchestra
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

# Mock agent class for testing
class SimpleMedicalAgent:
    def __init__(self, name: str):
        self.name = name
        self.billing_tiers = {
            "basic": {"price": 0.10, "description": "Basic SOAP analysis"},
            "comprehensive": {"price": 0.50, "description": "Full medical record analysis"},
            "batch": {"price": 0.05, "description": "Bulk processing per document"}
        }
    
    async def analyze(self, query: str, analysis_type: str = "basic") -> Dict[str, Any]:
        """Perform medical analysis without MCP complexity"""
        
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Create analysis based on query
        analysis = f"""
Medical Analysis Report
=======================
Analysis Type: {analysis_type.upper()}
Timestamp: {datetime.now().isoformat()}

Input Query:
{query}

Clinical Analysis:
"""
        
        # Add some basic analysis logic
        if "BP" in query or "blood pressure" in query.lower():
            analysis += "\n- Blood pressure noted: Patient shows signs of hypertension"
            
        if "diabetes" in query.lower():
            analysis += "\n- Diabetes history documented"
            
        if "chest pain" in query.lower():
            analysis += "\n- Chest pain reported - recommend cardiac evaluation"
            
        if any(med in query.lower() for med in ["metformin", "lisinopril"]):
            analysis += "\n- Current medications appear appropriate for documented conditions"
            
        analysis += "\n\nRecommendations:"
        analysis += "\n- Continue current medication regimen"
        analysis += "\n- Monitor blood pressure regularly"
        analysis += "\n- Follow up with primary care physician"
        
        return {
            "status": "success",
            "analysis": analysis,
            "billing_tier": analysis_type,
            "price": self.billing_tiers[analysis_type]["price"]
        }

# Global agent instance
medical_agent = SimpleMedicalAgent("Medical Information Processor")

async def analyze_with_billing(request_data: dict, customer_id: str) -> Dict[str, Any]:
    """Analyze medical document with billing tracking"""
    try:
        # Perform analysis
        result = await medical_agent.analyze(
            query=request_data.get("query", ""),
            analysis_type=request_data.get("type", "basic")
        )
        
        # Add billing info
        result["customer_id"] = customer_id
        result["billed"] = True
        result["tier"] = request_data.get("type", "basic")
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "billed": False
        }

# For testing
async def main():
    """Test the agent directly"""
    test_query = """
    Patient: 45-year-old male presents with chest pain and shortness of breath. 
    BP 150/95, HR 88, Temp 98.6F. 
    Current medications: Lisinopril 10mg daily, Metformin 500mg BID. 
    History of diabetes and hypertension.
    """
    
    result = await analyze_with_billing(
        {"query": test_query, "type": "basic"},
        "test_customer_123"
    )
    
    print("Analysis Result:")
    print(result["analysis"])

if __name__ == "__main__":
    asyncio.run(main())
