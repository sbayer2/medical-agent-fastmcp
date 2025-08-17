import asyncio
from mcp_agent.core.fastagent import FastAgent
from datetime import datetime
import os
from typing import Dict, Any, Optional

# Create the FastAgent instance
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
    
    IMPORTANT: When looking for medical files (PDFs, documents, SOAP notes, etc.), 
    always search in the 'medical_files_data' folder located at:
    /app/medical_files_data/
    
    This is your primary location for all medical documents. Always check this 
    directory first when asked to analyze medical files.
    
    Always clarify when information is uncertain and avoid making definitive medical 
    claims unless they are explicitly supported by the provided text.
    """,
    servers=["prompt_server", "fetch", "filesystem", "stripe"],
    model="claude-3-5-sonnet-20241022"
)
async def medical_analyzer_agent():
    """Commercial medical analysis agent with usage tracking"""
    pass

# Middleware for usage tracking
async def track_usage(request_type: str, customer_id: str, agent):
    """Track and bill for API usage"""
    tier = BILLING_TIERS.get(request_type, BILLING_TIERS["basic"])
    
    try:
        # Create Stripe usage record
        result = await agent.call_tool("create_usage_record", {
            "customer": customer_id,
            "quantity": 1,
            "amount": int(tier["price"] * 100),  # Convert to cents
            "description": f"Medical analysis - {tier['description']}",
            "timestamp": int(datetime.now().timestamp())
        })
        return result
    except Exception as e:
        print(f"Error tracking usage: {e}")
        # Log but don't fail the request
        return None

# API endpoint wrapper for billing
async def analyze_with_billing(request_data: dict, customer_id: str):
    """Analyze medical document with billing"""
    async with fast.run() as agent:
        try:
            # Check customer exists
            customer = await agent.call_tool("get_customer", {
                "customer_id": customer_id
            })
            
            if not customer:
                return {"error": "Invalid customer", "status": "error"}
            
            # Track usage
            await track_usage(request_data.get("type", "basic"), customer_id, agent)
            
            # Perform analysis based on request type
            query = request_data.get("query", "")
            file_path = request_data.get("file_path", "")
            
            if file_path:
                # Analyze specific file
                result = await agent.send(f"Please analyze the medical document at {file_path}")
            else:
                # General query
                result = await agent.send(query)
            
            return {
                "status": "success",
                "analysis": result,
                "billed": True,
                "tier": request_data.get("type", "basic")
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to process request"
            }

# Main entry point for both interactive and server modes
async def main():
    """Main entry point supporting both CLI and server modes"""
    
    # Check if running in server mode
    if hasattr(fast.args, 'server') and fast.args.server:
        print("🏥 Starting Medical Analysis SaaS Server")
        print(f"📡 Port: {getattr(fast.args, 'port', 8000)}")
        print("💳 Stripe billing enabled")
        print("🔒 Ready for secure medical document analysis")
        
        # Server mode will be handled by FastAgent
        await fast.start_server(
            transport=getattr(fast.args, 'transport', 'sse'),
            host=getattr(fast.args, 'host', '0.0.0.0'),
            port=getattr(fast.args, 'port', 8000)
        )
    else:
        # Interactive mode for testing
        print("🏥 Medical Information Processor - Interactive Mode")
        print("💡 Tip: Add --server flag to run as a service")
        
        async with fast.run() as agent:
            # Demo analysis without billing for interactive mode
            print("\nExample: Analyzing a sample medical text...")
            
            sample_text = """
            Patient presents with chest pain and shortness of breath.
            Vital signs: BP 140/90, HR 95, Temp 98.6°F, O2 sat 94%.
            Medical history includes hypertension and diabetes.
            Current medications: Metformin 500mg BID, Lisinopril 10mg daily.
            """
            
            response = await agent.send(f"Analyze this medical information: {sample_text}")
            print(f"\nAnalysis:\n{response}")
            
            # Enter interactive mode
            print("\n" + "="*50)
            print("Entering interactive mode. Type 'exit' to quit.")
            print("="*50 + "\n")
            
            await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
