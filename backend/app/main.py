from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import engine, Base, SessionLocal
from backend.data.seed_data import seed_database
from backend.app.api.router import api_router
from backend.app.websocket.analysis_ws import analysis_websocket_endpoint


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database tables are created & seed initial match data
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)
    yield
    # Shutdown logic (if any)


app = FastAPI(
    title="VisionVAR Intelligence Platform API",
    description=(
        "AI-Powered Football Video Intelligence and VAR Analysis Platform Backend.\n\n"
        "Provides REST APIs for video ingestion, session processing, match timelines, "
        "and player telemetry, alongside WebSockets for live video intelligence streams."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API
app.include_router(api_router, prefix=settings.API_V1_STR)


# Mount WebSocket for live analysis
@app.websocket("/ws/analysis/{session_id}")
async def websocket_analysis(websocket: WebSocket, session_id: str):
    await analysis_websocket_endpoint(websocket, session_id)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
