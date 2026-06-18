from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from app.services.url_analyzer import URLAnalyzer
from typing import Optional

router = APIRouter()

class URLRequest(BaseModel):
    url: str

class URLResponse(BaseModel):
    url: str
    is_malicious: bool
    confidence_score: float
    analysis_time_ms: Optional[float] = None

@router.post("/check", response_model=URLResponse)
async def check_url(request: URLRequest):
    import time
    
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    analyzer = URLAnalyzer()
    
    start_time = time.time()
    result = await analyzer.analyze_url(request.url)
    analysis_time = (time.time() - start_time) * 1000
    
    return URLResponse(
        url=result["url"],
        is_malicious=result["is_malicious"],
        confidence_score=result["confidence_score"],
        analysis_time_ms=analysis_time
    )

@router.get("/history")
async def get_scan_history(limit: int = 10):
    from app.db.database import SessionLocal
    from app.db.models import URLScan
    
    db = SessionLocal()
    try:
        scans = db.query(URLScan).order_by(URLScan.scan_date.desc()).limit(limit).all()
        return [
            {
                "url": scan.url,
                "is_malicious": scan.is_malicious,
                "confidence": scan.confidence_score,
                "date": scan.scan_date.isoformat()
            }
            for scan in scans
        ]
    finally:
        db.close()
