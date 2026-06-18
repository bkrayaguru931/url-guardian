from fastapi import APIRouter
from app.api.v1.endpoints import url_check, batch_check

api_router = APIRouter()

api_router.include_router(url_check.router, prefix="/url", tags=["URL Check"])
api_router.include_router(batch_check.router, prefix="/batch", tags=["Batch Check"])
