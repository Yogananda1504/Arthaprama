"""
Arthaprama FastAPI Production Server.

This module acts as the server entry point containing ASGI application routing,
global error hooks, and CORS middleware configurations for the IPO analysis API.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.mcp_server import create_mcp_sse_app
from backend.routes.ipo import router as ipo_router
from backend.schemas import ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("arthaprama-api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager for startup and shutdown events.

    Args:
        app: The FastAPI application instance.

    Yields:
        None
    """
    # Startup
    logger.info("Starting Arthaprama IPO Analysis API...")
    logger.info("Loading mathematical engines...")

    # Import core modules to verify they load correctly
    from arthaprama.config import get_profile
    from arthaprama.ipo import growth, risk, valuation, scoring

    logger.info("All modules loaded successfully.")
    logger.info("MCP SSE transport available at /sse")
    logger.info("Arthaprama API is ready to accept requests.")

    yield

    # Shutdown
    logger.info("Shutting down Arthaprama API...")
    logger.info("Cleanup complete.")


def create_application() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    app = FastAPI(
        title="Arthaprama IPO Analysis API",
        description="""
## Arthaprama (अर्थप्रमा) - Accurate Financial Knowledge

A production-ready technical analytical engine designed to calculate **Growth, Risk, Valuation, 
and composite scores explicitly for Indian IPOs (Initial Public Offerings)**.

### Features

- **100-Point Scoring Matrix**: Comprehensive evaluation across four pillars
  - Growth (30 points): Revenue/profit growth, margins, ROE, ROCE
  - Risk (30 points): Debt ratios, liquidity, cash flow quality, promoter metrics
  - Valuation (30 points): P/E, P/B, EV/EBITDA, PEG, peer comparisons
  - IPO Quality (10 points): Dilution, promoter holding, pledge ratio

- **Investor Profiles**: Multiple evaluation strategies
  - Balanced: Equal weighting across all pillars
  - Conservative: Higher weight on risk mitigation
  - Aggressive Growth: Higher weight on growth metrics
  - Deep Value: Higher weight on valuation metrics

- **Mathematical Precision**: All calculations use `decimal.Decimal` for accuracy

### Philosophy

"Prama" means accurate, valid, and foundational knowledge. This library prioritizes 
strict data validation, explicit precision, and comprehensive error handling.

### Compliance Note

This is a mathematical engine only. It does not provide investment advice or 
explicit "BUY"/"SELL" recommendations.
        """,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:8080",
            "https://*.arthaprama.io",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(ipo_router)

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Global exception handler for unhandled exceptions.

        Args:
            request: The incoming request.
            exc: The raised exception.

        Returns:
            JSONResponse with error details.
        """
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="InternalServerError",
                message="An unexpected error occurred. Please try again later.",
                detail=str(exc) if app.debug else None,
            ).model_dump(),
        )

    # Root endpoint
    @app.get(
        "/",
        tags=["Health"],
        summary="API Health Check",
        description="Returns API status and version information.",
    )
    async def root() -> dict[str, str]:
        """Root endpoint returning API information."""
        return {
            "name": "Arthaprama IPO Analysis API",
            "version": "0.1.0",
            "status": "healthy",
            "docs": "/docs",
            "redoc": "/redoc",
        }

    # Health check endpoint
    @app.get(
        "/health",
        tags=["Health"],
        summary="Health Check",
        description="Simple health check endpoint for monitoring.",
    )
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy"}

    # Mount MCP SSE transport under /sse using the MCP app's native route map.
    app.mount("/", create_mcp_sse_app())

    return app


# Create the application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
