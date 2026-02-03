"""File read, write, and edit endpoints."""
import difflib
from typing import Union

from fastapi import APIRouter, Body, HTTPException

from app.dependencies import normalize_path
from app.schemas import (
    DiffResponse,
    EditFileRequest,
    ReadFileRequest,
    ReadFileResponse,
    SuccessResponse,
    WriteFileRequest,
)

router = APIRouter(
    tags=["files"],
    responses={404: {"description": "Not found"}},
)


@router.post("/read_file", response_model=ReadFileResponse, summary="Read a file")
async def read_file(data: ReadFileRequest = Body(...)):
    """Read the entire contents of a file and return as JSON."""
    path = normalize_path(data.path)
    try:
        file_content = path.read_text(encoding="utf-8")
        return ReadFileResponse(content=file_content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {data.path}")
    except PermissionError:
        raise HTTPException(status_code=403, detail=f"Permission denied for file: {data.path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file {data.path}: {str(e)}")


@router.post("/write_file", response_model=SuccessResponse, summary="Write to a file")
async def write_file(data: WriteFileRequest = Body(...)):
    """Write content to a file, overwriting if it exists. Returns JSON success message."""
    path = normalize_path(data.path)
    try:
        path.write_text(data.content, encoding="utf-8")
        return SuccessResponse(message=f"Successfully wrote to {data.path}")
    except PermissionError:
        raise HTTPException(status_code=403, detail=f"Permission denied to write to {data.path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write to {data.path}: {str(e)}")


@router.post(
    "/edit_file",
    response_model=Union[SuccessResponse, DiffResponse],
    summary="Edit a file with diff",
)
async def edit_file(data: EditFileRequest = Body(...)):
    """Apply a list of edits to a text file. Returns JSON success message or JSON diff on dry-run."""
    path = normalize_path(data.path)
    try:
        original = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {data.path}")
    except PermissionError:
        raise HTTPException(status_code=403, detail=f"Permission denied to read file: {data.path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file {data.path} for editing: {str(e)}")

    modified = original
    try:
        for edit in data.edits:
            if edit.oldText not in modified:
                raise HTTPException(
                    status_code=400,
                    detail=f"Edit failed: oldText not found in content: '{edit.oldText[:50]}...'",
                )
            modified = modified.replace(edit.oldText, edit.newText, 1)

        if data.dryRun:
            diff_output = difflib.unified_diff(
                original.splitlines(keepends=True),
                modified.splitlines(keepends=True),
                fromfile=f"a/{data.path}",
                tofile=f"b/{data.path}",
            )
            return DiffResponse(diff="".join(diff_output))

        path.write_text(modified, encoding="utf-8")
        return SuccessResponse(message=f"Successfully edited file {data.path}")

    except PermissionError:
        raise HTTPException(status_code=403, detail=f"Permission denied to write edited file: {data.path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write edited file {data.path}: {str(e)}")
