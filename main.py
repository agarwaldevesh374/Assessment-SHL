# ============================================================================
# CELL 12: Setup FastAPI
# ============================================================================
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import re
from fastapi.responses import HTMLResponse

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

@app.get("/", response_class=HTMLResponse)
def home():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SHL Assessment Recommender</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.1em; opacity: 0.9; }}
        .api-info {{
            background: rgba(255,255,255,0.1);
            padding: 10px;
            border-radius: 5px;
            margin-top: 15px;
            font-size: 0.9em;
        }}
        .content {{ padding: 40px; }}
        .search-box {{ margin-bottom: 30px; }}
        .search-box textarea {{
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1em;
            font-family: inherit;
            resize: vertical;
            min-height: 100px;
        }}
        .search-box textarea:focus {{
            outline: none;
            border-color: #667eea;
        }}
        .search-btn {{
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
            transition: transform 0.2s;
        }}
        .search-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        .search-btn:disabled {{ opacity: 0.6; cursor: not-allowed; }}
        .loading {{
            text-align: center;
            padding: 40px;
            color: #667eea;
            display: none;
        }}
        .loading.active {{ display: block; }}
        .spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        .results {{ display: none; }}
        .results.active {{ display: block; }}
        .assessment-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
            transition: transform 0.2s;
        }}
        .assessment-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .assessment-title {{
            font-size: 1.3em;
            color: #333;
            margin-bottom: 10px;
            font-weight: bold;
        }}
        .assessment-meta {{
            display: flex;
            gap: 20px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }}
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 5px;
            color: #666;
            font-size: 0.9em;
        }}
        .assessment-desc {{
            color: #555;
            line-height: 1.6;
            margin-bottom: 10px;
        }}
        .assessment-link {{
            display: inline-block;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            margin-top: 10px;
        }}
        .assessment-link:hover {{ text-decoration: underline; }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            background: #667eea;
            color: white;
            border-radius: 20px;
            font-size: 0.85em;
            margin-right: 5px;
            margin-top: 5px;
        }}
        .example-queries {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .example-queries h3 {{
            margin-bottom: 10px;
            color: #333;
        }}
        .example-btn {{
            display: inline-block;
            padding: 8px 15px;
            background: white;
            border: 2px solid #667eea;
            color: #667eea;
            border-radius: 5px;
            margin: 5px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.2s;
        }}
        .example-btn:hover {{
            background: #667eea;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> SHL Assessment Recommender</h1>
            <p>Find the perfect assessments for your hiring needs</p>
            <div class="api-info">
                 API: {api_url}
            </div>
        </div>
        
        <div class="content">
            <div class="example-queries">
                <h3>📋 Example Queries (Click to try):</h3>
                <button class="example-btn" onclick="tryExample('I am hiring for Java developers who can also collaborate effectively with my business teams.')">
                    Java + Collaboration
                </button>
                <button class="example-btn" onclick="tryExample('Looking to hire mid-level professionals who are proficient in Python, SQL and JavaScript.')">
                    Python, SQL, JavaScript
                </button>
                <button class="example-btn" onclick="tryExample('Need sales representatives with strong communication and customer service skills.')">
                    Sales + Communication
                </button>
            </div>
            
            <div class="search-box">
                <textarea id="queryInput" placeholder="Enter job description or requirements...

Example: I am hiring for Java developers who can also collaborate effectively with my business teams."></textarea>
                <button class="search-btn" onclick="getRecommendations()">
                    Get Recommendations
                </button>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <h3> Finding best assessments for you...</h3>
            </div>
            
            <div class="results" id="results"></div>
        </div>
    </div>
    
    <script>
        const API_URL = '{api_url}';
        
        function tryExample(query) {{
            document.getElementById('queryInput').value = query;
            getRecommendations();
        }}
        
        async function getRecommendations() {{
            const query = document.getElementById('queryInput').value.trim();
            
            if (!query) {{
                alert('Please enter a job description or query');
                return;
            }}
            
            document.getElementById('loading').classList.add('active');
            document.getElementById('results').classList.remove('active');
            document.querySelector('.search-btn').disabled = true;
            
            try {{
                const response = await fetch(API_URL + '/recommend', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ query: query }})
                }});
                
                if (!response.ok) throw new Error('Failed to get recommendations');
                
                const data = await response.json();
                displayResults(data.recommended_assessments);
                
            }} catch (error) {{
                console.error('Error:', error);
                alert('Error getting recommendations. Please try again.');
            }} finally {{
                document.getElementById('loading').classList.remove('active');
                document.querySelector('.search-btn').disabled = false;
            }}
        }}
        
        function displayResults(assessments) {{
            const resultsDiv = document.getElementById('results');
            
            if (!assessments || assessments.length === 0) {{
                resultsDiv.innerHTML = '<p>No assessments found.</p>';
                resultsDiv.classList.add('active');
                return;
            }}
            
            let html = `<h2 style="margin-bottom: 20px;">📋 Recommended Assessments (${{assessments.length}})</h2>`;
            
            assessments.forEach((assessment, index) => {{
                html += `
                    <div class="assessment-card">
                        <div class="assessment-title">${{index + 1}}. ${{assessment.name}}</div>
                        <div class="assessment-meta">
                            <div class="meta-item"> ${{assessment.duration}} min</div>
                            <div class="meta-item"> Remote: ${{assessment.remote_support}}</div>
                            <div class="meta-item"> Adaptive: ${{assessment.adaptive_support}}</div>
                        </div>
                        ${{assessment.test_type.map(type => `<span class="badge">${{type}}</span>`).join('')}}
                        <div class="assessment-desc">${{assessment.description}}</div>
                        <a href="${{assessment.url}}" target="_blank" class="assessment-link">
                            View Assessment Details →
                        </a>
                    </div>
                `;
            }});
            
            resultsDiv.innerHTML = html;
            resultsDiv.classList.add('active');
        }}
        
        document.getElementById('queryInput').addEventListener('keydown', function(e) {{
            if (e.key === 'Enter' && e.ctrlKey) {{
                getRecommendations();
            }}
        }});
    </script>
</body>
</html>"""


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



