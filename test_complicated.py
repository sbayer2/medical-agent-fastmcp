import asyncio
import os
# Import the actual function, not the wrapped tool
from medical_mcp_server import mcp

# Get the underlying function from the tool registry
analyze_medical_document = None
for tool in mcp._tools.values():
    if tool.name == "analyze_medical_document":
        analyze_medical_document = tool.func
        break

async def test_complicated():
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
    
    result = await analyze_medical_document(test_doc, 'complicated', 'test_001')
    print('✅ Complicated Analysis Complete')
    print(f'Type: {result.get("analysis_type")}')
    print(f'Price: ${result.get("billing_info", {}).get("price")}')
    print(f'Features: {len(result.get("analysis_features", []))}')
    if 'error' in result:
        print(f'Error: {result["error"]}')
    else:
        print(f'Success: {len(result.get("ai_analysis", ""))} chars')
        print(f'Model: {result.get("model_used")}')

if __name__ == "__main__":
    asyncio.run(test_complicated())