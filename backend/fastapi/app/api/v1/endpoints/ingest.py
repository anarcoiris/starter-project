from fastapi import APIRouter, Depends
from app.services.ingestion_service import IngestionService
from app.api.deps import get_ingestion_service

router = APIRouter()

@router.post("/trigger")
async def trigger_ingestion(service: IngestionService = Depends(get_ingestion_service)):
    """
    Manually triggers the news ingestion process from RSS sources.
    Uses AI to refactor the content and assigns stock images if missing.
    """
    new_articles = await service.ingest_all()
    return {
        "status": "success",
        "new_articles_count": new_articles,
        "message": f"Successfully ingested {new_articles} new articles."
    }
