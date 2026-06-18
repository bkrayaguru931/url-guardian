from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from app.db.database import Base
from datetime import datetime

class URLScan(Base):
    __tablename__ = "url_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text, nullable=False)
    is_malicious = Column(Boolean, nullable=False)
    confidence_score = Column(Float)
    threat_type = Column(String(50))
    scan_date = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String(20))
    
class APIUsage(Base):
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String(100))
    endpoint = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
    response_time_ms = Column(Integer)
