"""Entity and observation endpoints."""
from fastapi import APIRouter, Body, HTTPException

from app.schemas import (
    AddObservationsRequest,
    CreateEntitiesRequest,
    DeleteEntitiesRequest,
    DeleteObservationsRequest,
)
from app.storage import read_graph_file, save_graph

router = APIRouter(
    tags=["entities"],
    responses={404: {"description": "Not found"}},
)


@router.post("/create_entities", summary="Create multiple entities in the graph")
def create_entities(req: CreateEntitiesRequest = Body(...)):
    graph = read_graph_file()
    existing_names = {e.name for e in graph.entities}
    new_entities = [e for e in req.entities if e.name not in existing_names]
    graph.entities.extend(new_entities)
    save_graph(graph)
    return new_entities


@router.post("/add_observations", summary="Add new observations to existing entities")
def add_observations(req: AddObservationsRequest = Body(...)):
    graph = read_graph_file()
    results = []

    for obs in req.observations:
        name = obs.entityName.lower()
        contents = obs.contents
        entity = next((e for e in graph.entities if e.name == name), None)
        if not entity:
            raise HTTPException(status_code=404, detail=f"Entity {name} not found")
        added = [c for c in contents if c not in entity.observations]
        entity.observations.extend(added)
        results.append({"entityName": name, "addedObservations": added})

    save_graph(graph)
    return results


@router.post("/delete_entities", summary="Delete entities and associated relations")
def delete_entities(req: DeleteEntitiesRequest = Body(...)):
    graph = read_graph_file()
    graph.entities = [e for e in graph.entities if e.name not in req.entityNames]
    graph.relations = [
        r
        for r in graph.relations
        if r.from_ not in req.entityNames and r.to not in req.entityNames
    ]
    save_graph(graph)
    return {"message": "Entities deleted successfully"}


@router.post("/delete_observations", summary="Delete specific observations from entities")
def delete_observations(req: DeleteObservationsRequest = Body(...)):
    graph = read_graph_file()

    for deletion in req.deletions:
        name = deletion.entityName.lower()
        to_delete = deletion.observations
        entity = next((e for e in graph.entities if e.name == name), None)
        if entity:
            entity.observations = [
                obs for obs in entity.observations if obs not in to_delete
            ]

    save_graph(graph)
    return {"message": "Observations deleted successfully"}
