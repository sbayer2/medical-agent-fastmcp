#!/usr/bin/env python3
"""
Test script to demonstrate proper prompt-guided tool orchestration
"""
import asyncio
from medical_agent_enhanced import analyze_with_billing
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_prompt_guided_analysis():
    """Test the full prompt-guided workflow"""
    
    print("="*70)
    print("Testing Prompt-Guided Medical Analysis")
    print("="*70)
    
    # Test 1: File analysis with prompt guidance
    print("\n1. Testing file analysis with prompt server guidance...")
    
    request = {
        "type": "basic",
        "file_path": "/app/medical_files_data/sample_soap_note.txt"
    }
    
    result = await analyze_with_billing(request, "cus_test_123")
    
    print("\nResult:")
    print(f"Status: {result.get('status')}")
    print(f"Billed: {result.get('billed')}")
    print(f"Price: ${result.get('price')}")
    
    if result.get('analysis'):
        print(f"\nAnalysis Preview: {result['analysis'][:500]}...")
    
    # Test 2: What happens without prompt guidance (the problem you mentioned)
    print("\n" + "="*70)
    print("2. Demonstrating the problem without prompt guidance...")
    print("="*70)
    
    # This would show how the LLM might hallucinate or skip tools
    print("Without prompt_server, the LLM might:")
    print("- Make up file contents instead of reading them")
    print("- Skip the filesystem tool entirely")
    print("- Provide generic medical advice without real data")
    print("- Forget to use the stripe tool for billing")
    
    # Test 3: Query analysis with fetch tool
    print("\n" + "="*70)
    print("3. Testing query that requires external fetch...")
    print("="*70)
    
    request = {
        "type": "comprehensive",
        "query": "What are the latest CDC guidelines for COVID-19 treatment?"
    }
    
    # This should trigger the fetch tool through prompt guidance
    result = await analyze_with_billing(request, "cus_test_123")
    
    print(f"\nFetch-guided result: {result.get('status')}")

async def demonstrate_tool_orchestration():
    """Show how prompts guide tool selection"""
    
    from mcp_agent.core.fastagent import FastAgent
    
    fast = FastAgent("Demo")
    
    @fast.agent(
        name="demo_agent",
        instruction="You are a demo agent showing tool orchestration",
        servers=["prompt_server", "filesystem"],
        model="claude-3-5-sonnet-20241022"
    )
    async def demo():
        pass
    
    async with fast.run() as agent:
        print("\n" + "="*70)
        print("Demonstrating Tool Orchestration")
        print("="*70)
        
        # Show how prompt_server guides tool usage
        test_scenarios = [
            {
                "query": "Show me what prompts are available",
                "expected": "Should list medical_processor, patient_summary, etc."
            },
            {
                "query": "What tools should I use to analyze a medical file?",
                "expected": "Should recommend filesystem first, then analysis"
            },
            {
                "query": "How do I handle billing for a medical analysis?",
                "expected": "Should recommend stripe tool with specific steps"
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\nQuery: {scenario['query']}")
            print(f"Expected: {scenario['expected']}")
            
            response = await agent.send(scenario['query'])
            print(f"Response: {response[:200]}...")

if __name__ == "__main__":
    print("🧠 Prompt-Guided Medical Agent Test")
    print("This demonstrates why prompt_server is critical for proper tool usage\n")
    
    # Run the tests
    asyncio.run(test_prompt_guided_analysis())
    
    # Optionally show tool orchestration
    # asyncio.run(demonstrate_tool_orchestration())
