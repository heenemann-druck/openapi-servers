"""FastAPI app: Wiki.js OpenAPI proxy for Open WebUI tools."""
from fastapi import APIRouter, Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import WIKIJS_API_KEY
from app.schemas import (
    CreatePageRequest,
    GetPageRequest,
    ListPagesResponse,
    PageInfo,
    UpdatePageRequest,
)
from app.wikijs_client import (
    create_page as wikijs_create_page,
    get_page_by_path,
    list_pages as wikijs_list_pages,
    update_page as wikijs_update_page,
)

app = FastAPI(
    title="Wiki.js Proxy API",
    version="0.1.0",
    description="OpenAPI proxy for Wiki.js: get, list, create, and update wiki pages. Register this server in Open WebUI Admin → Tools as a Global Tool Server.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(
    tags=["wikijs"],
    responses={400: {"description": "Invalid input"}, 502: {"description": "Wiki.js API error"}},
)


@router.get("/", include_in_schema=False)
async def root():
    """Root redirect for OpenAPI discovery; some clients request / first."""
    return {"message": "Wiki.js Proxy API", "openapi": "/openapi.json", "docs": "/docs"}


def _require_api_key():
    if not WIKIJS_API_KEY or not WIKIJS_API_KEY.strip():
        raise HTTPException(
            status_code=503,
            detail="WIKIJS_API_KEY is not set. Set it in the proxy environment and create an API key in Wiki.js Administration → API Access.",
        )


@router.post(
    "/get_page",
    response_model=PageInfo,
    summary="Get a wiki page by path",
    description="Fetch a single Wiki.js page by its path (e.g. /HW/Workstation-01). Returns id, path, title, content, description.",
)
async def get_page(request: GetPageRequest = Body(...)):
    _require_api_key()
    page = await get_page_by_path(request.path)
    if not page:
        raise HTTPException(status_code=404, detail=f"Page not found: {request.path}")
    return PageInfo(
        id=page.get("id"),
        path=page.get("path", ""),
        title=page.get("title", ""),
        content=page.get("content"),
        description=page.get("description"),
    )


@router.post(
    "/list_pages",
    response_model=ListPagesResponse,
    summary="List all wiki pages",
    description="Return a list of all pages (id, path, title, description). Useful to discover existing pages before get_page or update_page.",
)
async def list_pages():
    _require_api_key()
    items = await wikijs_list_pages()
    pages = [
        PageInfo(id=p.get("id"), path=p.get("path", ""), title=p.get("title", ""), description=p.get("description"))
        for p in items
    ]
    return ListPagesResponse(pages=pages)


@router.post(
    "/create_page",
    summary="Create a new wiki page",
    description="Create a new page in Wiki.js. Provide path (e.g. /DOC/MyPage), title, and content. Optional: description, locale, tags.",
)
async def create_page(request: CreatePageRequest = Body(...)):
    _require_api_key()
    try:
        result = await wikijs_create_page(
            path=request.path,
            title=request.title,
            content=request.content,
            description=request.description,
            locale=request.locale,
            is_published=request.is_published,
            tags=request.tags,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Wiki.js API error: {e}")
    data = result.get("data", {}).get("pages", {}).get("create", {})
    resp = data.get("responseResult", {})
    if not resp.get("succeeded"):
        msg = resp.get("message") or resp.get("slug") or "Create failed"
        raise HTTPException(status_code=400, detail=msg)
    page = data.get("page", {})
    return {
        "message": "Page created successfully",
        "id": page.get("id"),
        "path": page.get("path"),
        "title": page.get("title"),
    }


@router.post(
    "/update_page",
    summary="Update an existing wiki page",
    description="Update a page by its ID (from get_page or list_pages). Provide at least one of content, title, or description.",
)
async def update_page(request: UpdatePageRequest = Body(...)):
    _require_api_key()
    if not any([request.content, request.title, request.description]):
        raise HTTPException(
            status_code=400,
            detail="At least one of content, title, or description must be provided.",
        )
    try:
        result = await wikijs_update_page(
            page_id=request.page_id,
            content=request.content,
            title=request.title,
            description=request.description,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Wiki.js API error: {e}")
    data = result.get("data", {}).get("pages", {}).get("update", {})
    resp = data.get("responseResult", {})
    if not resp.get("succeeded"):
        msg = resp.get("message") or resp.get("slug") or "Update failed"
        raise HTTPException(status_code=400, detail=msg)
    page = data.get("page", {})
    return {
        "message": "Page updated successfully",
        "id": page.get("id"),
        "path": page.get("path"),
        "title": page.get("title"),
    }


app.include_router(router)
