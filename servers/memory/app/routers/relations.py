"""Relation endpoints."""
from fastapi import APIRouter, Body

from app.schemas import CreateRelationsRequest, DeleteRelationsRequest
from app.storage import read_graph_file, save_graph

router = APIRouter(
    tags=["relations"],
    responses={404: {"description": "Not found"}},
)


@router.post("/create_relations", summary="Create multiple relations between entities")
def create_relations(req: CreateRelationsRequest = Body(...)):
    graph = read_graph_file()
    existing = {(r.from_, r.to, r.relationType) for r in graph.relations}
    new = [r for r in req.relations if (r.from_, r.to, r.relationType) not in existing]
    graph.relations.extend(new)
    save_graph(graph)
    return new


@router.post("/delete_relations", summary="Delete relations from the graph")
def delete_relations(req: DeleteRelationsRequest = Body(...)):
    graph = read_graph_file()
    del_set = {(r.from_, r.to, r.relationType) for r in req.relations}
    graph.relations = [
        r for r in graph.relations if (r.from_, r.to, r.relationType) not in del_set
    ]
    save_graph(graph)
    return {"message": "Relations deleted successfully"}
