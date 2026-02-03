"""Directory listing, tree, search, and create endpoints."""
import os
import pathlib

from fastapi import APIRouter, Body, HTTPException

from app.dependencies import normalize_path
from app.schemas import (
    CreateDirectoryRequest,
    DirectoryTreeRequest,
    ListDirectoryRequest,
    SearchContentRequest,
    SearchFilesRequest,
    SuccessResponse,
)
from config import ALLOWED_DIRECTORIES

router = APIRouter(
    tags=["directories"],
    responses={404: {"description": "Not found"}},
)


@router.post("/create_directory", response_model=SuccessResponse, summary="Create a directory")
async def create_directory(data: CreateDirectoryRequest = Body(...)):
    """Create a new directory recursively. Returns JSON success message."""
    dir_path = normalize_path(data.path)
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        return SuccessResponse(message=f"Successfully created directory {data.path}")
    except PermissionError:
        raise HTTPException(status_code=403, detail=f"Permission denied to create directory {data.path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create directory {data.path}: {str(e)}")


@router.post("/list_directory", summary="List a directory")
async def list_directory(data: ListDirectoryRequest = Body(...)):
    """List contents of a directory."""
    dir_path = normalize_path(data.path)
    if not dir_path.is_dir():
        raise HTTPException(status_code=400, detail="Provided path is not a directory")

    listing = []
    for entry in dir_path.iterdir():
        entry_type = "directory" if entry.is_dir() else "file"
        listing.append({"name": entry.name, "type": entry_type})
    return listing


@router.post("/directory_tree", summary="Recursive directory tree")
async def directory_tree(data: DirectoryTreeRequest = Body(...)):
    """Recursively return a tree structure of a directory."""
    base_path = normalize_path(data.path)

    def build_tree(current: pathlib.Path):
        entries = []
        for item in current.iterdir():
            entry = {
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
            }
            if item.is_dir():
                entry["children"] = build_tree(item)
            entries.append(entry)
        return entries

    return build_tree(base_path)


@router.post("/search_files", summary="Search for files")
async def search_files(data: SearchFilesRequest = Body(...)):
    """Search files and directories matching a pattern."""
    base_path = normalize_path(data.path)
    results = []

    for root, dirs, files in os.walk(base_path):
        root_path = pathlib.Path(root)
        excluded = False
        for pattern in data.excludePatterns:
            if pathlib.Path(root).match(pattern):
                excluded = True
                break
        if excluded:
            continue
        for item in files + dirs:
            if data.pattern.lower() in item.lower():
                result_path = root_path / item
                if any(str(result_path).startswith(alt) for alt in ALLOWED_DIRECTORIES):
                    results.append(str(result_path))

    return {"matches": results or ["No matches found"]}


@router.post("/search_content", summary="Search for content within files")
async def search_content(data: SearchContentRequest = Body(...)):
    """Search for text content within files in a specified directory."""
    base_path = normalize_path(data.path)
    results = []
    search_query_lower = data.search_query.lower()

    if not base_path.is_dir():
        raise HTTPException(status_code=400, detail="Provided path is not a directory")

    iterator = base_path.rglob(data.file_pattern) if data.recursive else base_path.glob(data.file_pattern)

    for item_path in iterator:
        if item_path.is_file():
            try:
                with item_path.open("r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        if search_query_lower in line.lower():
                            results.append(
                                {
                                    "file_path": str(item_path),
                                    "line_number": line_num,
                                    "line_content": line.strip(),
                                }
                            )
            except Exception:
                continue

    return {"matches": results or ["No matches found"]}
