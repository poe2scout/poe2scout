from fastapi import FastAPI, Request, Depends
from dotenv import load_dotenv
import os
from services.repositories.base_repository import BaseRepository
from contextlib import asynccontextmanager
import sys
import asyncio
from . import ApiServiceConfig
import uvicorn
from services.apiService.routes import item_router
from services.apiService.routes import league_router
import logging
import time
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse, Response
from slowapi.middleware import SlowAPIMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()    
config = ApiServiceConfig.load_from_env()
IS_LOCAL = os.getenv("local", "false").lower() == "true"

def get_real_ip(request: Request) -> str:
    real_ip = request.headers.get("cf-connecting-ip")

    if real_ip:
        return real_ip

    return get_remote_address(request)

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    client_ip = get_real_ip(request)
    logger.warning(
        f"Custom Handler: Rate limit exceeded - IP: {client_ip}, "
        f"Path: {request.url.path}, "
        f"Method: {request.method}, "
        f"Limit Details: {exc.detail}"
    )

    response = JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": f"Limit: {exc.detail}. Please try again later."
        }
    )

    response = request.app.state.limiter._inject_headers(
        response, request.state.view_rate_limit
    )

    return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    await BaseRepository.init_pool(config.dbstring)
    yield

app = FastAPI(
        title='Jupiter Api',
        version='1.0',
        description='Jupiter Api',
        docs_url='/swagger',
        root_path='/api',
        lifespan=lifespan
    )

limiter = Limiter(
    key_func=get_real_ip,
    application_limits=["100/minute"],
    headers_enabled=True
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

if IS_LOCAL:
    logger.info("Running in local mode, enabling CORS for localhost.")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            ], 
        allow_credentials=True,
        allow_methods=["*"], 
        allow_headers=["*"], 
    )

# Import and include routers
app.include_router(item_router)
app.include_router(league_router)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request started: {request.method} {request.url}")
    logger.info(f"Client IP: {request.client.host if request.client else 'Unknown'}")
    logger.info(f"Headers: {request.headers}")
    
    # Process the request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response details
    logger.info(f"Request completed: {request.method} {request.url}")
    logger.info(f"Status code: {response.status_code}")
    logger.info(f"Processing time: {process_time:.3f} seconds")
    
    return response

@app.get("/")
def read_root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        proxy_headers=True,
        forwarded_allow_ips='*'
    )