"""FastAPI application: CORS and router registration."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.confirmations import cleanup_stale_confirmation_file
from app.routers import directories, files, path_ops


@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_stale_confirmation_file()
    yield


app = FastAPI(
    title="Secure Filesystem API",
    version="0.1.1",
    description="A secure file manipulation server for reading, editing, writing, listing, and searching files with access restrictions.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files.router)
app.include_router(directories.router)
app.include_router(path_ops.router)
