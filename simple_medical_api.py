"""
Simple Medical Analysis API without MCP for testing
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

app = FastAPI(
    title="Medical Analysis API",
    description="AI-powered medical document analysis (Simplified)",
    version="3.0.1"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store analysis jobs for async processing
analysis_jobs = {}

class AnalysisRequest(BaseModel):
    customer_id: str
    type: str = "basic"
    query: Optional[str] = None
    file_path: Optional[str] = None

class AnalysisResponse(BaseModel):
    status: str
    job_id: Optional[str] = None
    analysis: Optional[str] = None
    error: Optional[str] = None
    billed: Optional[bool] = None
    tier: Optional[str] = None
    price: Optional[float] = None

# Billing tiers
BILLING_TIERS = {
    "basic": {"price": 0.10, "description": "Basic SOAP analysis"},
    "comprehensive": {"price": 0.50, "description": "Full medical record analysis"},
    "batch": {"price": 0.05, "description": "Bulk processing per document"}
}

def analyze_medical_text(text: str, analysis_type: str) -> str:
    """Simple medical text analysis without MCP"""
    
    # Extract key medical information
    analysis = f"**Medical Analysis Report**\n"
    analysis += f"Analysis Type: {analysis_type.upper()}\n"
    analysis += f"Timestamp: {datetime.now().isoformat()}\n\n"
    
    # Look for vital signs
    if "BP" in text or "HR" in text or "Temp" in text:
        analysis += "**Vital Signs Detected:**\n"
        if "BP" in text:
            analysis += "- Blood Pressure mentioned\n"
        if "HR" in text:
            analysis += "- Heart Rate mentioned\n"
        if "Temp" in text:
            analysis += "- Temperature mentioned\n"
        analysis += "\n"
    
    # Look for medications
    if "mg" in text or "medication" in text.lower():
        analysis += "**Medications Noted:**\n"
        analysis += "- Medication dosages detected in the text\n\n"
    
    # Look for symptoms
    symptoms = ["pain", "shortness of breath", "cough", "fever", "nausea"]
    found_symptoms = [s for s in symptoms if s in text.lower()]
    if found_symptoms:
        analysis += "**Symptoms Identified:**\n"
        for symptom in found_symptoms:
            analysis += f"- {symptom.title()}\n"
        analysis += "\n"
    
    # Add summary
    analysis += "**Summary:**\n"
    analysis += "This analysis is a simplified demonstration. "
    analysis += "In production, this would use AI-powered analysis with FastAgent and MCP.\n"
    
    return analysis

async def process_analysis_job(job_id: str, request: AnalysisRequest):
    """Process analysis in background"""
    try:
        # Simulate analysis
        if request.query:
            analysis_result = analyze_medical_text(request.query, request.type)
        elif request.file_path:
            analysis_result = f"File analysis for: {request.file_path}\n(File reading would be implemented with MCP filesystem server)"
        else:
            analysis_result = "No content provided for analysis"
        
        # Get billing info
        tier = BILLING_TIERS.get(request.type, BILLING_TIERS["basic"])
        
        # Store result
        analysis_jobs[job_id] = {
            "status": "success",
            "analysis": analysis_result,
            "billed": True,
            "tier": request.type,
            "price": tier["price"],
            "customer_id": request.customer_id
        }
    except Exception as e:
        analysis_jobs[job_id] = {
            "status": "error",
            "error": str(e),
            "billed": False
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "medical-agent", "mode": "simplified"}

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_document(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Submit medical document for analysis"""
    try:
        # For small queries, analyze immediately
        if request.query and len(request.query) < 500:
            analysis_result = analyze_medical_text(request.query, request.type)
            tier = BILLING_TIERS.get(request.type, BILLING_TIERS["basic"])
            
            return AnalysisResponse(
                status="success",
                analysis=analysis_result,
                billed=True,
                tier=request.type,
                price=tier["price"]
            )
        
        # For larger requests, use background processing
        job_id = str(uuid.uuid4())
        background_tasks.add_task(process_analysis_job, job_id, request)
        
        return AnalysisResponse(
            status="processing",
            job_id=job_id,
            tier=request.type
        )
        
    except Exception as e:
        return AnalysisResponse(
            status="error",
            error=str(e),
            billed=False
        )

@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    """Check analysis job status"""
    if job_id in analysis_jobs:
        return analysis_jobs[job_id]
    return {"status": "pending", "job_id": job_id}

@app.get("/api/billing/tiers")
async def get_billing_tiers():
    """Get available billing tiers"""
    return BILLING_TIERS

@app.get("/api/test-customer")
async def get_test_customer():
    """Get test customer info for development"""
    return {
        "customer_id": "cus_SSpdLLaCGuIao0",
        "name": "Medical Test Hospital",
        "email": "medical-test@example.com",
        "note": "Test customer created for medical agent development"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
