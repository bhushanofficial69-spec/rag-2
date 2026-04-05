import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from utils.logger import setup_logging, get_logger
from routers import health as health_router
from routers import ingest as ingest_router
from routers import query

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="CodeMind RAG API",
    version="0.2.0",
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

app.include_router(health_router.router)
app.include_router(ingest_router.router)
app.include_router(query.router)


@app.on_event("startup")
async def startup() -> None:
    logger.info("codemind_rag_api_starting", version="0.2.0")

    vector_db = None
    if settings.QDRANT_URL and settings.QDRANT_API_KEY:
        from services.vector_db import VectorDBClient
        vector_db = VectorDBClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            collection_name=settings.QDRANT_COLLECTION_NAME,
            dimension=settings.VECTOR_DIMENSION,
        )
        if vector_db.available:
            vector_db.create_collection_if_not_exists()
    else:
        logger.warning(
            "qdrant_not_configured",
            hint="Set QDRANT_URL and QDRANT_API_KEY env vars to enable vector storage",
        )

    from services.ingestion import IngestionService
    svc = IngestionService(vector_db=vector_db)

    health_router.set_vector_db(vector_db)
    ingest_router.set_ingestion_service(svc)

    logger.info(
        "startup_complete",
        qdrant="connected" if (vector_db and vector_db.available) else "not_configured",
    )


@app.on_event("shutdown")
async def shutdown() -> None:
    logger.info("codemind_rag_api_shutting_down")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
