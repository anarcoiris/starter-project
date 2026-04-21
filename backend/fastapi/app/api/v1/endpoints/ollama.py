import httpx
from fastapi import APIRouter, Request, Response
from app.core.config import settings

router = APIRouter()

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_ollama(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        url = f"{settings.ollama_host}/{path}"
        
        # Collect headers and body
        headers = dict(request.headers)
        # Remove host header to avoid conflicts
        headers.pop("host", None)
        
        # Read request body
        content = await request.body()
        
        # Forward request to Ollama
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=content,
            params=request.query_params,
            timeout=None # Ollama can be slow
        )
        
        # Return response to client
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
