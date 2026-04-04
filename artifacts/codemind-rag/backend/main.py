import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils.logger import setup_logging, get_logger
from routers import health, ingest, query

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="CodeMind RAG API",
    version="0.1.0",
    description="Intelligent Codebase Search Engine — GitHub Repo Ingestion & RAG Query API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:23968",
        "http://127.0.0.1:23968",
        "https://*.replit.dev",
        "https://*.riker.replit.dev",
        "https://*.repl.co",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(ingest.router)
app.include_router(query.router)


@app.on_event("startup")
async def startup() -> None:
    logger.info("codemind_rag_api_starting", version="0.1.0")


@app.on_event("shutdown")
async def shutdown() -> None:
    logger.info("codemind_rag_api_shutting_down")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
