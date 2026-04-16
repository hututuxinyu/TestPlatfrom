from fastapi import APIRouter

from app.api.v1 import auth, executions, scripts

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(scripts.router)
api_router.include_router(executions.router)
