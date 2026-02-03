"""Pydantic request/response schemas."""
from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class ReadFileRequest(BaseModel):
    path: str = Field(..., description="Path to the file to read")


class WriteFileRequest(BaseModel):
    path: str = Field(
        ..., description="Path to write to. Existing file will be overwritten."
    )
    content: str = Field(..., description="UTF-8 encoded text content to write.")


class EditOperation(BaseModel):
    oldText: str = Field(
        ..., description="Text to find and replace (exact match required)"
    )
    newText: str = Field(..., description="Replacement text")


class EditFileRequest(BaseModel):
    path: str = Field(..., description="Path to the file to edit.")
    edits: List[EditOperation] = Field(..., description="List of edits to apply.")
    dryRun: bool = Field(
        False, description="If true, only return diff without modifying file."
    )


class CreateDirectoryRequest(BaseModel):
    path: str = Field(
        ...,
        description="Directory path to create. Intermediate dirs are created automatically.",
    )


class ListDirectoryRequest(BaseModel):
    path: str = Field(..., description="Directory path to list contents for.")


class DirectoryTreeRequest(BaseModel):
    path: str = Field(
        ..., description="Directory path for which to return recursive tree."
    )


class SearchFilesRequest(BaseModel):
    path: str = Field(..., description="Base directory to search in.")
    pattern: str = Field(
        ..., description="Filename pattern (case-insensitive substring match)."
    )
    excludePatterns: Optional[List[str]] = Field(
        default=[], description="Patterns to exclude."
    )


class SearchContentRequest(BaseModel):
    path: str = Field(..., description="Base directory to search within.")
    search_query: str = Field(..., description="Text content to search for (case-insensitive).")
    recursive: bool = Field(
        default=True, description="Whether to search recursively in subdirectories."
    )
    file_pattern: Optional[str] = Field(
        default="*", description="Glob pattern to filter files to search within (e.g., '*.py')."
    )


class DeletePathRequest(BaseModel):
    path: str = Field(..., description="Path to the file or directory to delete.")
    recursive: bool = Field(
        default=False,
        description="If true and path is a directory, delete recursively. Required if directory is not empty.",
    )
    confirmation_token: Optional[str] = Field(
        default=None,
        description="Token required for confirming deletion after initial request.",
    )


class MovePathRequest(BaseModel):
    source_path: str = Field(..., description="The current path of the file or directory.")
    destination_path: str = Field(..., description="The new path for the file or directory.")


class GetMetadataRequest(BaseModel):
    path: str = Field(..., description="Path to the file or directory to get metadata for.")


class SuccessResponse(BaseModel):
    message: str = Field(..., description="Success message indicating the operation was completed.")


class ReadFileResponse(BaseModel):
    content: str = Field(..., description="UTF-8 encoded text content of the file.")


class DiffResponse(BaseModel):
    diff: str = Field(..., description="Unified diff output comparing original and modified content.")


class ConfirmationRequiredResponse(BaseModel):
    message: str = Field(..., description="Message indicating confirmation is required.")
    confirmation_token: str = Field(..., description="Token needed for the confirmation step.")
    expires_at: datetime = Field(..., description="UTC timestamp when the token expires.")
