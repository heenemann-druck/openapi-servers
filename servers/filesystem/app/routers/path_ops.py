"""Path operations: delete, move, metadata, list allowed directories."""
import secrets
import shutil
from datetime import datetime, timedelta, timezone
from typing import Union

from fastapi import APIRouter, Body, HTTPException

from app.confirmations import (
    CONFIRMATION_TTL_SECONDS,
    load_confirmations,
    save_confirmations,
)
from app.dependencies import normalize_path
from app.schemas import (
    ConfirmationRequiredResponse,
    DeletePathRequest,
    GetMetadataRequest,
    MovePathRequest,
    SuccessResponse,
)
from config import ALLOWED_DIRECTORIES

router = APIRouter(
    tags=["path-ops"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/delete_path",
    response_model=Union[SuccessResponse, ConfirmationRequiredResponse],
    summary="Delete a file or directory (two-step confirmation)",
)
async def delete_path(data: DeletePathRequest = Body(...)):
    """
    Delete a specified file or directory using a two-step confirmation process.
    1. Initial request (without confirmation_token): Returns a confirmation token.
    2. Confirmation request (with token): Executes the deletion if the token is valid.
    Use 'recursive=True' to delete non-empty directories.
    """
    pending_confirmations = load_confirmations()
    path = normalize_path(data.path)
    now = datetime.now(timezone.utc)

    if data.confirmation_token:
        if data.confirmation_token not in pending_confirmations:
            raise HTTPException(status_code=400, detail="Invalid or expired confirmation token.")

        confirmation_data = pending_confirmations[data.confirmation_token]
        if now > confirmation_data["expiry"]:
            del pending_confirmations[data.confirmation_token]
            save_confirmations(pending_confirmations)
            raise HTTPException(status_code=400, detail="Confirmation token has expired.")

        if confirmation_data["path"] != data.path or confirmation_data["recursive"] != data.recursive:
            raise HTTPException(
                status_code=400,
                detail="Request parameters (path, recursive) do not match the original request for this token.",
            )

        del pending_confirmations[data.confirmation_token]
        save_confirmations(pending_confirmations)

        try:
            if not path.exists():
                raise HTTPException(status_code=404, detail=f"Path not found: {data.path}")

            if path.is_file():
                path.unlink()
                return SuccessResponse(message=f"Successfully deleted file: {data.path}")
            elif path.is_dir():
                if data.recursive:
                    shutil.rmtree(path)
                    return SuccessResponse(message=f"Successfully deleted directory recursively: {data.path}")
                else:
                    try:
                        path.rmdir()
                        return SuccessResponse(message=f"Successfully deleted empty directory: {data.path}")
                    except OSError as e:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Directory not empty. Use 'recursive=True' to delete non-empty directories. Original error: {e}",
                        )
            else:
                raise HTTPException(status_code=400, detail=f"Path is not a file or directory: {data.path}")

        except PermissionError:
            raise HTTPException(status_code=403, detail=f"Permission denied to delete {data.path}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete {data.path}: {e}")

    else:
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"Path not found: {data.path}")

        token = secrets.token_hex(3)[:5]
        expiry_time = now + timedelta(seconds=CONFIRMATION_TTL_SECONDS)
        pending_confirmations[token] = {
            "path": data.path,
            "recursive": data.recursive,
            "expiry": expiry_time,
        }
        save_confirmations(pending_confirmations)
        confirmation_message = f"`Confirm deletion of file: {data.path} with token {token}`"
        return ConfirmationRequiredResponse(
            message=confirmation_message,
            confirmation_token=token,
            expires_at=expiry_time,
        )


@router.post("/move_path", response_model=SuccessResponse, summary="Move or rename a file or directory")
async def move_path(data: MovePathRequest = Body(...)):
    """Move or rename a file or directory. Both paths must be within the allowed directories."""
    source = normalize_path(data.source_path)
    destination = normalize_path(data.destination_path)

    try:
        if not source.exists():
            raise HTTPException(status_code=404, detail=f"Source path not found: {data.source_path}")

        shutil.move(str(source), str(destination))
        return SuccessResponse(message=f"Successfully moved '{data.source_path}' to '{data.destination_path}'")

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied for move operation involving '{data.source_path}' or '{data.destination_path}'",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to move '{data.source_path}' to '{data.destination_path}': {e}",
        )


@router.post("/get_metadata", summary="Get file or directory metadata")
async def get_metadata(data: GetMetadataRequest = Body(...)):
    """Retrieve metadata for a specified file or directory path."""
    path = normalize_path(data.path)

    try:
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"Path not found: {data.path}")

        stat_result = path.stat()
        file_type = "file" if path.is_file() else "directory" if path.is_dir() else "other"
        mod_time = datetime.fromtimestamp(stat_result.st_mtime, tz=timezone.utc).isoformat()
        try:
            create_time = datetime.fromtimestamp(stat_result.st_birthtime, tz=timezone.utc).isoformat()
        except AttributeError:
            create_time = datetime.fromtimestamp(stat_result.st_ctime, tz=timezone.utc).isoformat()

        metadata = {
            "path": str(path),
            "type": file_type,
            "size_bytes": stat_result.st_size,
            "modification_time_utc": mod_time,
            "creation_time_utc": create_time,
            "last_metadata_change_time_utc": datetime.fromtimestamp(stat_result.st_ctime, tz=timezone.utc).isoformat(),
        }
        return metadata

    except PermissionError:
        raise HTTPException(status_code=403, detail=f"Permission denied to access metadata for {data.path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metadata for {data.path}: {e}")


@router.get("/list_allowed_directories", summary="List access-permitted directories")
async def list_allowed_directories():
    """Show all directories this server can access."""
    return {"allowed_directories": ALLOWED_DIRECTORIES}
