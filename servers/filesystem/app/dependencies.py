"""Shared dependencies and path validation."""
import os
import pathlib

from fastapi import HTTPException

from config import ALLOWED_DIRECTORIES


def normalize_path(requested_path: str) -> pathlib.Path:
    """Resolve and validate path against allowed directories. Raises HTTPException 403 if denied."""
    requested = pathlib.Path(os.path.expanduser(requested_path)).resolve()
    for allowed in ALLOWED_DIRECTORIES:
        if str(requested).lower().startswith(allowed.lower()):
            return requested
    raise HTTPException(
        status_code=403,
        detail={
            "error": "Access Denied",
            "requested_path": str(requested),
            "message": "Requested path is outside allowed directories.",
            "allowed_directories": ALLOWED_DIRECTORIES,
        },
    )
