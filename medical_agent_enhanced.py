import asyncio
from mcp_agent.core.fastagent import FastAgent
from datetime import datetime
import os
from typing import Dict, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
    You are a specialized medical information processing assistant with access to multiple tools.
    
    CRITICAL RULES:
    1. ALWAYS consult the prompt_server FIRST to get guidance on how to handle requests
    2. NEVER analyze medical files without first reading them using the filesystem tool
    3. NEVER make up medical information - use fetch tool for external resources if needed
    4. ALWAYS track billing using the stripe tool for commercial requests
    
    Tool Usage Workflow:
    1. When asked to analyze a medical document:
       - First: Ask prompt_server for "analyze_file" guidance
       - Second: Use filesystem to read the actual file content
       - Third: Apply the medical_processor prompt from prompt_server
       - Finally: Use stripe for billing if in commercial mode
    
    2. When asked for medical guidelines or research:
       - First: Ask prompt_server for "fetch_guidelines" guidance
       - Second: Use fetch tool to retrieve actual information
       - NEVER provide medical advice without real sources
    
    3. For patient summaries:
       - First: Get "patient_summary" guidance from prompt_server
       - Second: Read patient data using filesystem
       - Third: Format according to prompt template
    
    Remember: The prompt_server is your guide - it tells you which tools to use and when.
    """,
    servers=["prompt_server", "fetch", "filesystem", "stripe"],
    model="claude-3-5-sonnet-20241022"
)
async def medical_analyzer_agent():
    """Medical analysis agent with prompt-guided tool orchestration"""
    pass

# Middleware for prompt-guided analysis
async def guided_analysis(agent, task_type: str, **kwargs):
    """Use prompt server to guide the analysis process"""
    try:
        # Step 1: Get guidance from prompt server
        guidance = await agent.call_tool("tools/guidance", {"task": task_type})
        logger.info(f"Received guidance: {guidance}")
        
        # Step 2: Get the appropriate prompt if specified
        if guidance.get("guidance", {}).get("prompt"):
            prompt_name = guidance["guidance"]["prompt"]
            prompt_template = await agent.call_tool("prompts/get", {
                "name": prompt_name,
                "context": kwargs
            })
            logger.info(f"Using prompt template: {prompt_name}")
        
        # Step 3: Follow the guided steps
        steps = guidance.get("guidance", {}).get("steps", [])
        for step in steps:
            logger.info(f"Executing step: {step}")
        
        return guidance
        
    except Exception as e:
        logger.error(f"Error in guided analysis: {e}")
        return None

# Main analysis function with proper tool orchestration
async def analyze_with_billing(request_data: dict, customer_id: str):
    """Analyze medical document with prompt-guided tool usage"""
    try:
        async with fast.run() as agent:
            # Determine task type
            file_path = request_data.get("file_path")
            query = request_data.get("query", "")
            
            if file_path:
                # File analysis workflow
                logger.info("Starting file analysis workflow")
                
                # Get guidance on how to analyze files
                guidance_prompt = """
                I need to analyze a medical document. 
                First, tell me which tools I should use and in what order.
                The file is located at: {file_path}
                """.format(file_path=file_path)
                
                response = await agent.send(guidance_prompt)
                logger.info(f"Agent guidance response: {response}")
                
                # Now execute the analysis with explicit tool usage
                analysis_prompt = f"""
                Following the guidance, I will now:
                1. Use the filesystem tool to read the medical document at {file_path}
                2. Apply medical analysis using the medical_processor prompt
                3. Track billing with stripe tool
                
                Please analyze the medical document at {file_path}
                """
                
                result = await agent.send(analysis_prompt)
                
            else:
                # Direct query analysis
                logger.info("Starting direct query analysis")
                
                # For direct queries, still use prompt guidance
                guidance_prompt = f"""
                I need to analyze this medical information: {query}
                What tools and prompts should I use?
                """
                
                guidance = await agent.send(guidance_prompt)
                logger.info(f"Guidance for query: {guidance}")
                
                # Analyze with guidance
                result = await agent.send(f"Analyze this medical information: {query}")
            
            # Get analysis type and billing tier
            analysis_type = request_data.get("type", "basic")
            tier = BILLING_TIERS.get(analysis_type, BILLING_TIERS["basic"])
            
            # Track usage with Stripe
            billing_prompt = f"""
            Please use the stripe tool to record this billing event:
            - Customer: {customer_id}
            - Service: Medical analysis ({analysis_type})
            - Amount: ${tier["price"]}
            """
            
            billing_result = await agent.send(billing_prompt)
            logger.info(f"Billing tracked: {billing_result}")
            
            return {
                "status": "success",
                "analysis": result,
                "billed": True,
                "tier": analysis_type,
                "price": tier["price"],
                "customer_id": customer_id
            }
            
    except Exception as e:
        logger.error(f"Error in analysis: {e}")
        return {
            "status": "error",
            "error": str(e),
            "billed": False
        }

# Interactive mode for testing
async def main():
    """Main entry point with prompt-guided orchestration"""
    
    if hasattr(fast.args, 'server') and fast.args.server:
        print("🏥 Starting Medical Analysis SaaS Server")
        print("🧠 Prompt-guided tool orchestration enabled")
        print("🔧 Available tools: prompt_server, filesystem, fetch, stripe")
        
        await fast.start_server(
            transport=getattr(fast.args, 'transport', 'sse'),
            host=getattr(fast.args, 'host', '0.0.0.0'),
            port=getattr(fast.args, 'port', 8000)
        )
    else:
        # Interactive mode
        print("🏥 Medical Information Processor - Prompt-Guided Mode")
        print("🧠 Using prompt_server for tool orchestration")
        
        async with fast.run() as agent:
            # Demo the prompt-guided workflow
            print("\nDemonstrating prompt-guided analysis...")
            
            # First, show available prompts
            prompts_response = await agent.send("List available prompts from prompt_server")
            print(f"Available prompts: {prompts_response}")
            
            # Show tool guidance
            guidance_response = await agent.send(
                "Get tool guidance for analyzing a medical file"
            )
            print(f"Tool guidance: {guidance_response}")
            
            # Interactive mode
            print("\n" + "="*50)
            print("Entering interactive mode. Type 'exit' to quit.")
            print("Try: 'Analyze the SOAP note at /app/medical_files_data/sample_soap_note.txt'")
            print("="*50 + "\n")
            
            await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
