"""
Enterprise Research Assistant RAG — FastAPI Application Entry Point.
"""
import os
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.config.settings import settings
from app.utils.logger import get_logger
from app.utils.database import init_db
from app.api import documents_router, reports_router, search_router, system_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Initialize database
    init_db()
    logger.info("Database initialized")

    # Log configuration
    logger.info(f"Primary LLM: {settings.PRIMARY_LLM} ({settings.GEMINI_MODEL})")
    logger.info(f"Fallback LLM: OpenAI ({settings.OPENAI_MODEL})")
    logger.info(f"Embedding: {settings.PRIMARY_EMBEDDING}")
    logger.info(f"ChromaDB: {settings.CHROMA_PERSIST_DIR}")
    logger.info(f"Reports dir: {settings.REPORTS_DIR}")

    # Warm up vector store
    try:
        from app.vectorstore.chroma_store import ChromaVectorStore
        vs = ChromaVectorStore()
        logger.info(f"ChromaDB ready: {vs.count()} chunks indexed")
    except Exception as e:
        logger.warning(f"ChromaDB warmup warning: {e}")

    yield

    logger.info("Shutting down Enterprise RAG...")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Enterprise Research Assistant RAG — Automated structured PDF report generation "
        "from document corpora using Gemini, ChromaDB, FlashRank, and ReAct reasoning."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ──────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def add_request_timing(request: Request, call_next):
    """Add response time header to all requests."""
    start = time.time()
    response = await call_next(request)
    process_time = (time.time() - start) * 1000
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    logger.info(f"{request.method} {request.url.path} - {request.client.host if request.client else 'unknown'}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} -> {response.status_code}")
    return response


# ── Global exception handler ────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


# ── Routers ─────────────────────────────────────────────────────────────────

app.include_router(documents_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")


# ── Root endpoint ───────────────────────────────────────────────────────────

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "frontend")

@app.get("/", tags=["Root"], response_class=HTMLResponse)
async def root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return JSONResponse(content={"error": "Frontend not found", "api_docs": "/docs"})


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "timestamp": time.time()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1,
        log_level="debug" if settings.DEBUG else "info",
    )
