import asyncio
from mcp_agent.core.fastagent import FastAgent
from datetime import datetime
import os
from typing import Dict, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Check for secrets file
if os.path.exists("/app/fastagent.secrets.yaml"):
    logger.info("Found fastagent.secrets.yaml")
else:
    logger.warning("fastagent.secrets.yaml not found")

# Create the FastAgent instance
try:
    fast = FastAgent("Medical Information Processor", config_path="fastagent.config.yaml")
    logger.info("FastAgent created successfully")
except Exception as e:
    logger.error(f"Failed to create FastAgent: {e}")
    raise

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
    
    IMPORTANT: Medical files are located in /app/medical_files_data/
    
    Always maintain HIPAA compliance and avoid making definitive diagnoses.
    """,
    servers=["filesystem"],  # Only using available MCP servers
    model="claude-3-5-sonnet-20241022"
)
async def medical_analyzer_agent():
    """Medical analysis agent"""
    pass

async def analyze_document(query: str, file_path: Optional[str] = None):
    """Analyze a medical document or query"""
    try:
        logger.info(f"Starting analysis with query='{query}', file_path='{file_path}'")
        async with fast.run() as agent:
            if file_path:
                # Use filesystem server to read the file
                logger.info(f"Requesting analysis of file: {file_path}")
                prompt = f"Please read and analyze the medical document at {file_path}"
            else:
                prompt = f"Please analyze this medical information: {query}"
            
            logger.info(f"Sending to agent: {prompt}")
            response = await agent.send(prompt)
            logger.info("Analysis received from agent")
            return {
                "status": "success",
                "analysis": response
            }
    except Exception as e:
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
        return {
            "status": "error",
            "error": str(e),
            "billed": False
        }

# For direct testing
async def test_agent():
    """Test the agent directly"""
    print("Testing Medical Agent with MCP servers...")
    
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
