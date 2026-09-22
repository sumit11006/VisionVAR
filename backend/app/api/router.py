from fastapi import APIRouter
from backend.app.api.endpoints import health, videos, sessions, matches, cv_analysis

api_router = APIRouter()

# 1. Health
api_router.include_router(health.router)

# 2. Videos
api_router.include_router(videos.router, prefix="/videos")

# 3. Analysis Sessions
api_router.include_router(sessions.router, prefix="/analysis")

# 4. Matches, Events, Players, and CV Placeholders
api_router.include_router(matches.router, prefix="/matches")
api_router.include_router(cv_analysis.router, prefix="/matches")
