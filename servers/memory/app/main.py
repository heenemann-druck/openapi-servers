"""FastAPI application: CORS and router registration."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import entities, graph, relations

app = FastAPI(
    title="Knowledge Graph Server",
    version="1.0.0",
    description="A structured knowledge graph memory system that supports entity and relation storage, observation tracking, and manipulation.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(entities.router)
app.include_router(relations.router)
app.include_router(graph.router)
