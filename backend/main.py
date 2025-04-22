# main.py
from fastapi import FastAPI, HTTPException
from models.request_schema import QueryRequest, QueryMode
from services.query_service import get_summary_from_natural_language
from fastapi.middleware.cors import CORSMiddleware
from filter import run_filter_pipeline
from utils.enhanced_summary import enhance_summary

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:3000"] for stricter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/summary")
def get_summary(req: QueryRequest):
    try:
        summary = get_summary_from_natural_language(req.query)
        if summary == "None":
            raise ValueError("Summary not found.")
        enhanced_summary = enhance_summary(summary)
        return {"summary": enhanced_summary}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")

@app.post("/filter")
def filter_results(req: QueryRequest):  # Using QueryRequest consistently
    try:
        result = run_filter_pipeline(req.query)
        
        if not result or not result.get("papers"):
            raise ValueError("No papers found matching the criteria.")
        
        return {
            "papers": result["papers"],
            "total_count": result["total_count"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")