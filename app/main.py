"""Main FastAPI application."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.database import create_tables, check_database_connection
from app.routers import shortener, redirect, analytics
from app.utils.rate_limiter import limiter
from app.config import settings
from slowapi.errors import RateLimitExceeded

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting URL Shortener Service...")
    await create_tables()
    logger.info("Application startup complete")
    yield
    # Shutdown
    logger.info("Shutting down URL Shortener Service...")


# Create FastAPI app
app = FastAPI(
    title="URL Shortener Service",
    description="A production-ready URL shortening service with analytics and A/B testing",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiter state
app.state.limiter = limiter


# Root endpoint - defined BEFORE routers to prevent catch-all
@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to URL Shortener API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Health check endpoint - defined BEFORE routers to prevent catch-all
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint with database connectivity test."""
    db_healthy = await check_database_connection()

    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected"
    }


# Exception handlers
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    logger.warning(f"Rate limit exceeded for {request.client.host}")
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Include routers
app.include_router(shortener.router)
app.include_router(analytics.router)
app.include_router(redirect.router)  # Must be last due to catch-all pattern