"""Pydantic request/response schemas for Wiki.js proxy endpoints."""
from typing import List, Optional

from pydantic import BaseModel, Field


class GetPageRequest(BaseModel):
    path: str = Field(..., description="Wiki page path, e.g. /HW/Workstation-01 or /DOC/Build-Prozess")


class PageInfo(BaseModel):
    id: Optional[int] = None
    path: str = ""
    title: str = ""
    content: Optional[str] = None
    description: Optional[str] = None


class CreatePageRequest(BaseModel):
    path: str = Field(..., description="Page path, e.g. /HW/Workstation-01")
    title: str = Field(..., description="Page title")
    content: str = Field(..., description="Page content (Markdown supported)")
    description: str = Field("", description="Short description of the page")
    locale: str = Field("en", description="Locale code, e.g. en or de")
    is_published: bool = Field(True, description="Publish the page immediately")
    tags: List[str] = Field(default_factory=list, description="Tags for the page")


class UpdatePageRequest(BaseModel):
    page_id: int = Field(..., description="Wiki.js page ID (from get_page or list_pages)")
    content: Optional[str] = Field(None, description="New page content")
    title: Optional[str] = Field(None, description="New page title")
    description: Optional[str] = Field(None, description="New description")


class ListPagesResponse(BaseModel):
    pages: List[PageInfo] = Field(..., description="List of pages")
    message: Optional[str] = None
