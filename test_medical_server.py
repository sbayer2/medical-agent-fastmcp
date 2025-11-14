#!/usr/bin/env python3
"""
Test script for the Medical MCP Server with AI functionality
"""

import asyncio
import os
from medical_mcp_server import anthropic_client, openai_client, BILLING_TIERS

async def test_ai_providers():
    """Test AI provider connectivity"""
    print("🔬 Testing Medical MCP Server AI Integration")
    print("=" * 50)
    
    # Check environment variables
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    print(f"🔑 Anthropic API Key: {'✅ Configured' if anthropic_key else '❌ Missing'}")
    print(f"🔑 OpenAI API Key: {'✅ Configured' if openai_key else '❌ Missing'}")
    
    # Test AI client initialization
    print(f"🤖 Anthropic Client: {'✅ Initialized' if anthropic_client else '❌ Not Available'}")
    print(f"🤖 OpenAI Client: {'✅ Initialized' if openai_client else '❌ Not Available'}")
    
    # Test billing tiers
    print(f"💰 Billing Tiers: {len(BILLING_TIERS)} tiers configured")
    for tier, info in BILLING_TIERS.items():
        print(f"   - {tier}: ${info['price']} - {info['description']}")
    
    print("\n" + "=" * 50)
    
    if anthropic_client:
        print("🧠 Testing Claude Sonnet 4 Analysis...")
        try:
            test_content = """
            SOAP NOTE - Test Patient
            Chief Complaint: Chest pain
            Vital Signs: BP 140/90, HR 85, Temp 98.6°F
            Medications: Lisinopril 10mg daily
            Assessment: Hypertension, possible angina
            """
            
            message = anthropic_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=500,
                temperature=0.1,
                system="You are a medical AI. Extract vital signs, medications, and conditions from medical documents.",
                messages=[{
                    "role": "user", 
                    "content": f"Analyze this medical document:\n{test_content}"
                }]
            )
            
            print("✅ Claude Sonnet 4 Response Successful!")
            print(f"📊 Tokens Used: {message.usage.input_tokens} input, {message.usage.output_tokens} output")
            print(f"📝 Response Preview: {message.content[0].text[:200]}...")
            
        except Exception as e:
            print(f"❌ Claude Analysis Error: {str(e)}")
    
    elif openai_client:
        print("🧠 Testing OpenAI GPT-4 Analysis...")
        try:
            completion = await openai_client.chat.completions.create(
                model="gpt-4o",
                max_tokens=500,
                temperature=0.1,
                messages=[
                    {"role": "system", "content": "You are a medical AI. Extract vital signs, medications, and conditions."},
                    {"role": "user", "content": "Analyze this test medical document: BP 140/90, taking Lisinopril"}
                ]
            )
            
            print("✅ OpenAI GPT-4 Response Successful!")
            print(f"📊 Tokens Used: {completion.usage.total_tokens} total")
            print(f"📝 Response Preview: {completion.choices[0].message.content[:200]}...")
            
        except Exception as e:
            print(f"❌ OpenAI Analysis Error: {str(e)}")
    
    else:
        print("❌ No AI providers available for testing")
    
    print("\n🎉 Medical MCP Server Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_ai_providers())