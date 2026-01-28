import logging
import sys
from pathlib import Path

# ✅ ADD THIS: Fix import path when running directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scubagear_pricefinder.config import settings
from src.scubagear_pricefinder.db.connection import init_db
from src.scubagear_pricefinder.api.routes import products
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

init_db()

app = FastAPI(
    title="ScubaGear Price Finder",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}

@app.get("/")
def root():
    return {"name": "ScubaGear Price Finder", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.scubagear_pricefinder.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
