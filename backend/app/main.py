"""
Main application file for the Python Learning Platform backend.
"""
import os
import time
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import routers
from app.routes import health, exercises, chapters, token_tracking, execute

# Create FastAPI app
app = FastAPI(
    title="Python Learning Platform API",
    description="Backend API for the Python Learning Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions and return a consistent error response."""
    tb = traceback.format_exc()
    error_msg = f"Global exception: {str(exc)}\n{tb}"
    print(f"ERROR: {error_msg}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": tb if os.getenv("DEBUG", "false").lower() == "true" else None},
    )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and their processing time."""
    start_time = time.time()
    path = request.url.path
    print(f"REQUEST: {request.method} {path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        print(f"RESPONSE: {request.method} {path} - Status: {response.status_code} - Time: {process_time:.4f}s")
        return response
    except Exception as e:
        print(f"ERROR in middleware: {str(e)}")
        raise

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["Health"])
app.include_router(token_tracking.router, prefix="/api/token-tracking", tags=["Token Tracking"])
app.include_router(chapters.router, prefix="/api/chapters", tags=["Chapters"])
app.include_router(execute.router, prefix="/api", tags=["Code Execution"])

# Add direct token tracking paths for frontend compatibility
@app.get("/api/tokens")
async def tokens_redirect(request: Request):
    """Redirect token request to token_tracking router."""
    print(f"Redirected token request from: {request.url.path}")
    from app.routes.token_tracking import get_token_usage
    return await get_token_usage(request)

@app.post("/api/tokens")
async def tokens_update_redirect(request: Request):
    """Redirect token update to token_tracking router."""
    print(f"Redirected token update from: {request.url.path}")
    data = await request.json()
    from app.routes.token_tracking import update_token_usage
    return await update_token_usage(request, data)

# Import monitoring endpoints
try:
    from monitor import monitor
    
    # Add monitor endpoints
    @app.get("/api/monitor/heartbeat", tags=["Monitor"])
    async def heartbeat():
        """Register a heartbeat from the client to track browser connection"""
        return monitor.register_heartbeat()
    
    @app.get("/api/monitor/shutdown", tags=["Monitor"])
    async def shutdown():
        """Shutdown the server (triggered when browser closed)"""
        return monitor.shutdown_server()
    
    print("Browser activity monitor endpoints registered")
except ImportError:
    print("WARNING: Monitor module not found, browser activity tracking not available")

# Add exercises router last (it has catch-all routes)
app.include_router(exercises.router, prefix="/api", tags=["Exercises"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Python Learning Platform API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

# Run the app if executed directly
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    print(f"Starting server on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True) 