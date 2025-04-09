from fastapi import FastAPI, Request
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()    
config = ApiServiceConfig.load_from_env()
IS_LOCAL = os.getenv("local", "false").lower() == "true"

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
    logger.info(f"Client IP: {request.client.host}")
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
    uvicorn.run(app, host="0.0.0.0", port=5000)