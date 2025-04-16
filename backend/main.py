# main.py
from fastapi import FastAPI, HTTPException
from models.request_schema import QueryRequest
from services.query_service import get_summary_from_natural_language
from fastapi.middleware.cors import CORSMiddleware

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
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")
