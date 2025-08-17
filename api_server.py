"""
FastAPI wrapper for the Medical Agent with MCP
This properly integrates with FastAgent and MCP servers
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from typing import Optional
import uuid

# Import our MCP-enabled medical agent
from medical_agent_mcp import analyze_with_billing, BILLING_TIERS

app = FastAPI(
    title="Medical Analysis API",
    description="AI-powered medical document analysis with MCP integration",
    version="3.0.0"
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

async def process_analysis(job_id: str, request_data: dict, customer_id: str):
    """Background task to process analysis with MCP"""
    try:
        result = await analyze_with_billing(request_data, customer_id)
        analysis_jobs[job_id] = result
    except Exception as e:
        analysis_jobs[job_id] = {
            "status": "error",
            "error": str(e),
            "billed": False
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "medical-agent", "mcp": "enabled"}

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_document(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Submit medical document for analysis"""
    try:
        # For quick testing, try synchronous analysis first
        if (request.query and len(request.query) < 500) or request.file_path:  # Small queries or file analysis
            # Try direct analysis
            result = await analyze_with_billing(request.model_dump(), request.customer_id)
            if result["status"] == "success":
                return AnalysisResponse(**result)
        
        # For larger requests or if direct fails, use background processing
        job_id = str(uuid.uuid4())
        background_tasks.add_task(
            process_analysis, 
            job_id, 
            request.model_dump(), 
            request.customer_id
        )
        
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

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("🏥 Medical Analysis API Starting...")
    print("🔌 MCP Integration: Enabled")
    print("📍 Docs: http://localhost:8000/docs")
    print("💳 Test customer: /api/test-customer")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
