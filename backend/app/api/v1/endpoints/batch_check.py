from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.url_analyzer import URLAnalyzer

router = APIRouter()

class BatchRequest(BaseModel):
    urls: List[str]

class BatchResult(BaseModel):
    url: str
    is_malicious: bool
    confidence_score: float

@router.post("/check", response_model=List[BatchResult])
async def check_batch_urls(request: BatchRequest):
    if not request.urls:
        raise HTTPException(status_code=400, detail="URLs list is required")
    
    if len(request.urls) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 URLs per batch")
    
    analyzer = URLAnalyzer()
    results = []
    
    for url in request.urls:
        result = await analyzer.analyze_url(url)
        results.append(BatchResult(
            url=result["url"],
            is_malicious=result["is_malicious"],
            confidence_score=result["confidence_score"]
        ))
    
    return results
