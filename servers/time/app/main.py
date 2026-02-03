"""FastAPI application: CORS and router registration."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import time_routes

app = FastAPI(
    title="Secure Time Utilities API",
    version="1.0.0",
    description="Provides secure UTC/local time retrieval, formatting, timezone conversion, and comparison.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(time_routes.router)
