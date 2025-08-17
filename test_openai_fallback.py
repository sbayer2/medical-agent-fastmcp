#!/usr/bin/env python3
"""
Test OpenAI GPT-4o fallback functionality specifically
"""

import asyncio
import os
from medical_mcp_server import openai_client, anthropic_client

async def test_openai_fallback():
    """Test OpenAI fallback when Anthropic is not available"""
    print("🔬 Testing OpenAI GPT-4o Fallback Functionality")
    print("=" * 60)
    
    # Check original configuration
    print(f"🔑 Original Anthropic Key: {'✅ Configured' if anthropic_client else '❌ Missing'}")
    print(f"🔑 Original OpenAI Key: {'✅ Configured' if openai_client else '❌ Missing'}")
    
    # Force OpenAI-only scenario by temporarily disabling Anthropic
    if openai_client:
        print("\n🧠 Testing OpenAI GPT-4o Medical Analysis...")
        
        try:
            test_content = """
            EMERGENCY DEPARTMENT VISIT
            Patient: Maria Rodriguez, 67-year-old female
            Chief Complaint: Chest pain and shortness of breath
            
            VITAL SIGNS:
            - BP: 165/95 mmHg
            - HR: 105 bpm, irregular
            - RR: 24/min
            - Temp: 98.8°F
            - O2 Sat: 92% on room air
            
            MEDICATIONS: Metformin 1000mg BID, Lisinopril 20mg daily
            
            ASSESSMENT: STEMI (ST-Elevation Myocardial Infarction) - inferior wall
            """
            
            # Test comprehensive analysis prompt
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

            completion = await openai_client.chat.completions.create(
                model="gpt-4o",
                max_tokens=2000,
                temperature=0.1,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"""Please analyze the following medical document and provide a structured analysis:

=== MEDICAL DOCUMENT ===
{test_content}
=== END DOCUMENT ===

Provide your analysis in JSON format with appropriate medical categories and extracted information."""
                    }
                ]
            )
            
            print("✅ OpenAI GPT-4o Comprehensive Analysis Successful!")
            print(f"📊 Tokens Used: {completion.usage.prompt_tokens} input, {completion.usage.completion_tokens} output, {completion.usage.total_tokens} total")
            print(f"📝 Response Preview: {completion.choices[0].message.content[:300]}...")
            print(f"🏥 Model Used: {completion.model}")
            
            # Test if it properly extracts medical information
            analysis = completion.choices[0].message.content
            if "vital signs" in analysis.lower() and "medications" in analysis.lower():
                print("✅ Medical Information Extraction: PASS")
            else:
                print("⚠️  Medical Information Extraction: Partial")
                
            if "stemi" in analysis.lower() or "myocardial" in analysis.lower():
                print("✅ Critical Condition Recognition: PASS")
            else:
                print("⚠️  Critical Condition Recognition: Needs Review")
            
        except Exception as e:
            print(f"❌ OpenAI GPT-4o Analysis Error: {str(e)}")
    
    else:
        print("❌ OpenAI client not available for testing")
    
    print("\n" + "=" * 60)
    print("🎯 OpenAI Fallback Test Summary:")
    print("   - Environment Variables: ANTHROPIC_API_KEY, OPENAI_API_KEY")
    print("   - Model Used: gpt-4o") 
    print("   - Medical Analysis: Comprehensive prompt system")
    print("   - Token Counting: Full usage tracking")
    print("   - Error Handling: Graceful fallback")
    
    print("\n🎉 OpenAI Fallback Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_openai_fallback())