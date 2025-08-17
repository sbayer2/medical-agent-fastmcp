import asyncio
from mcp_agent.core.fastagent import FastAgent
from datetime import datetime
import os
from typing import Dict, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FastAgent instance - simplified version
logger.info("Creating FastAgent instance...")
fast = FastAgent("Medical Information Processor")

# Billing tiers configuration
BILLING_TIERS = {
    "basic": {"price": 0.10, "description": "Basic SOAP analysis"},
    "comprehensive": {"price": 0.50, "description": "Full medical record analysis"},
    "batch": {"price": 0.05, "description": "Bulk processing per document"}
}

@fast.agent(
    name="medical_analyzer",
    instruction="""
    You are a specialized medical information processing assistant. 
    Your role is to analyze medical texts, research papers, and patient information 
    to extract structured insights while maintaining accuracy and privacy.
    
    When analyzing medical information:
    1. Extract all vital signs (BP, HR, Temp, RR, O2 sat)
    2. List all medications with dosages
    3. Identify medical conditions and diagnoses
    4. Note any concerning findings
    5. Provide clear, structured summaries
    
    Always maintain HIPAA compliance and avoid making definitive diagnoses.
    """,
    servers=[],  # No MCP servers - just use the LLM directly
    model="claude-3-5-sonnet-20241022"
)
async def medical_analyzer_agent():
    """Medical analysis agent"""
    pass

async def analyze_document(query: str, file_path: Optional[str] = None):
    """Analyze a medical document or query"""
    try:
        logger.info("Starting document analysis...")
        async with fast.run() as agent:
            if file_path:
                # For now, just mention the file path in the prompt
                prompt = f"Please analyze this medical information (file: {file_path}): {query}"
            else:
                prompt = f"Please analyze this medical information: {query}"
            
            logger.info(f"Sending prompt to agent: {prompt[:100]}...")
            response = await agent.send(prompt)
            logger.info("Analysis complete")
            
            return {
                "status": "success",
                "analysis": response
            }
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

# Simplified billing function for API integration
async def analyze_with_billing(request_data: dict, customer_id: str):
    """Analyze medical document with billing"""
    try:
        # Get analysis type and determine price
        analysis_type = request_data.get("type", "basic")
        tier = BILLING_TIERS.get(analysis_type, BILLING_TIERS["basic"])
        
        logger.info(f"Processing {analysis_type} analysis for customer {customer_id}")
        
        # Perform analysis
        result = await analyze_document(
            query=request_data.get("query", ""),
            file_path=request_data.get("file_path")
        )
        
        # Add billing information
        if result["status"] == "success":
            result.update({
                "billed": True,
                "tier": analysis_type,
                "price": tier["price"],
                "customer_id": customer_id
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Billing analysis failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "billed": False
        }

# For direct testing
async def test_agent():
    """Test the agent directly"""
    print("Testing Medical Agent (simplified version)...")
    
    # Test with a simple query
    test_query = """
    Patient: 45-year-old male presents with chest pain and shortness of breath. 
    BP 150/95, HR 88, Temp 98.6F. 
    Current medications: Lisinopril 10mg daily, Metformin 500mg BID. 
    History of diabetes and hypertension.
    """
    
    result = await analyze_document(test_query)
    print(f"\nAnalysis Result:\n{result}")

if __name__ == "__main__":
    # Run test when called directly
    asyncio.run(test_agent())
