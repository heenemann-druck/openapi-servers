"""Graph read and query endpoints."""
from fastapi import APIRouter, Body

from app.schemas import KnowledgeGraph, OpenNodesRequest, SearchNodesRequest
from app.storage import read_graph_file

router = APIRouter(
    tags=["graph"],
    responses={404: {"description": "Not found"}},
)


@router.get("/read_graph", response_model=KnowledgeGraph, summary="Read entire knowledge graph")
def read_graph():
    return read_graph_file()


@router.post(
    "/search_nodes",
    response_model=KnowledgeGraph,
    summary="Search for nodes by keyword",
)
def search_nodes(req: SearchNodesRequest = Body(...)):
    graph = read_graph_file()
    entities = [
        e
        for e in graph.entities
        if req.query.lower() in e.name.lower()
        or req.query.lower() in e.entityType.lower()
        or any(req.query.lower() in o.lower() for o in e.observations)
    ]
    names = {e.name for e in entities}
    relations = [r for r in graph.relations if r.from_ in names and r.to in names]
    return KnowledgeGraph(entities=entities, relations=relations)


@router.post(
    "/open_nodes", response_model=KnowledgeGraph, summary="Open specific nodes by name"
)
def open_nodes(req: OpenNodesRequest = Body(...)):
    graph = read_graph_file()
    entities = [e for e in graph.entities if e.name in req.names]
    names = {e.name for e in entities}
    relations = [r for r in graph.relations if r.from_ in names and r.to in names]
    return KnowledgeGraph(entities=entities, relations=relations)
