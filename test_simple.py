#!/usr/bin/env python3
import os
import asyncio
from medical_mcp_server import anthropic_client

async def test_complicated_direct():
    """Test the complicated analysis directly with Claude Sonnet 4.5"""

    # API key should be set in environment variables before running
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your API key: export ANTHROPIC_API_KEY=your_key_here")
        return
    
    test_doc = '''SOAP NOTE - Complex Case
Patient: Smith, John A., 72-year-old male

SUBJECTIVE: 
Chief complaint: Worsening shortness of breath and chest tightness.
Current medications: Metformin 1000mg BID, Lisinopril 20mg daily, Warfarin 5mg daily

OBJECTIVE:
Vital Signs: BP 160/95, HR 102 irregular, O2 sat 88%
Labs: BNP 1250 pg/mL, Troponin I 0.8 ng/mL, INR 3.2

ASSESSMENT:
1. Acute on chronic CHF exacerbation  
2. Acute coronary syndrome
3. Atrial fibrillation with RVR

PLAN:
1. Admit for telemetry
2. IV diuresis
3. Cardiology consult'''

    system_prompt = """You are a specialized medical AI consultant performing advanced clinical analysis with multi-step reasoning.

MANDATORY MULTI-STEP WORKFLOW:

STEP 1: Document Validation & Completeness Assessment
- Verify medical document authenticity and completeness (score 1-10)
- Identify document type (SOAP, lab report, discharge summary, H&P, etc.)

STEP 2: Comprehensive Clinical Data Extraction  
- Extract ALL vital signs with temporal context and trends
- Complete medication reconciliation with drug interactions
- Laboratory values with reference ranges and clinical significance

STEP 3: Advanced Clinical Reasoning & Risk Stratification
- Chief complaint analysis with symptom constellation mapping
- Differential diagnosis reasoning with probability assessment
- Risk factor identification and comprehensive stratification

STEP 4: Quality Assurance & Critical Thinking
- Cross-reference findings for internal consistency
- Identify critical values requiring immediate intervention
- Flag potential medication errors, contraindications, allergies

STEP 5: Structured Clinical Intelligence Output
Provide comprehensive analysis in JSON format focusing on clinical accuracy and actionable specialist-level insights."""

    if anthropic_client:
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=3000,
            temperature=0.1,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": f"Analyze this medical document:\n\n{test_doc}"
            }]
        )
        
        print("✅ Complicated Analysis Test Complete")
        print(f"Model: claude-sonnet-4-5-20250929")
        print(f"Analysis Type: complicated")
        print(f"Price: $0.75")
        print(f"Response Length: {len(message.content[0].text)} chars")
        print(f"Tokens: {message.usage.input_tokens + message.usage.output_tokens}")
        print("\n--- Analysis Preview ---")
        print(message.content[0].text[:500] + "...")
    else:
        print("❌ Anthropic client not configured")

if __name__ == "__main__":
    asyncio.run(test_complicated_direct())