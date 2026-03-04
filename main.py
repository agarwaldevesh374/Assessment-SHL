# ============================================================================
# CELL 12: Setup FastAPI
# ============================================================================
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import re

# Create API endpoints

print("\n" + "="*80)
print(" SETTING UP FASTAPI")
print("="*80)

# Create FastAPI app
app = FastAPI(title="SHL Assessment Recommendation API")

# Load API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable for public URL
public_url = None

# Request/Response models
class QueryRequest(BaseModel):
    query: str

class AssessmentResponse(BaseModel):
    url: str
    name: str
    adaptive_support: str
    description: str
    duration: int
    remote_support: str
    test_type: List[str]

class RecommendationResponse(BaseModel):
    recommended_assessments: List[AssessmentResponse]

# API endpoints

@app.get("/")
def home():
    return {"message": "SHL Assessment Recommendation API is running"}
            
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api_url": public_url if public_url else "http://localhost:8000",
        "assessments_loaded": len(assessments)
    }

@app.post("/recommend", response_model=RecommendationResponse)
def recommend_api(request: QueryRequest):
    """Recommend assessments for a query"""
    try:
        if not request.query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        recommendations = recommend_assessments(request.query, top_n=TOP_N_RECOMMENDATIONS)
        
        assessment_responses = []
        for rec in recommendations:
            duration_str = rec.get('duration', '30 minutes')
            duration_minutes = int(re.search(r'\d+', duration_str).group()) if re.search(r'\d+', duration_str) else 30
            
            assessment_response = AssessmentResponse(
                url=rec.get('url', ''),
                name=rec.get('name', ''),
                adaptive_support=rec.get('adaptive_support', 'No'),
                description=rec.get('description', ''),
                duration=duration_minutes,
                remote_support=rec.get('remote_support', 'Yes'),
                test_type=[rec.get('test_type', '')]
            )
            assessment_responses.append(assessment_response)
        
        return RecommendationResponse(recommended_assessments=assessment_responses)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

print(" FastAPI configured!")

print("   Endpoints: /health, /recommend")


