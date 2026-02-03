"""Pydantic models for knowledge graph."""
from typing import List, Literal

from pydantic import BaseModel, Field


class Entity(BaseModel):
    name: str = Field(..., description="The name of the entity")
    entityType: str = Field(..., description="The type of the entity")
    observations: List[str] = Field(
        ..., description="An array of observation contents associated with the entity"
    )


class Relation(BaseModel):
    from_: str = Field(
        ...,
        alias="from",
        description="The name of the entity where the relation starts",
    )
    to: str = Field(..., description="The name of the entity where the relation ends")
    relationType: str = Field(..., description="The type of the relation")


class KnowledgeGraph(BaseModel):
    entities: List[Entity]
    relations: List[Relation]


class EntityWrapper(BaseModel):
    type: Literal["entity"]
    name: str
    entityType: str
    observations: List[str]


class RelationWrapper(BaseModel):
    type: Literal["relation"]
    from_: str = Field(..., alias="from")
    to: str
    relationType: str


class CreateEntitiesRequest(BaseModel):
    entities: List[Entity] = Field(..., description="List of entities to create")


class CreateRelationsRequest(BaseModel):
    relations: List[Relation] = Field(
        ..., description="List of relations to create. All must be in active voice."
    )


class ObservationItem(BaseModel):
    entityName: str = Field(
        ..., description="The name of the entity to add the observations to"
    )
    contents: List[str] = Field(
        ..., description="An array of observation contents to add"
    )


class DeletionItem(BaseModel):
    entityName: str = Field(
        ..., description="The name of the entity containing the observations"
    )
    observations: List[str] = Field(
        ..., description="An array of observations to delete"
    )


class AddObservationsRequest(BaseModel):
    observations: List[ObservationItem] = Field(
        ...,
        description="A list of observation additions, each specifying an entity and contents to add",
    )


class DeleteObservationsRequest(BaseModel):
    deletions: List[DeletionItem] = Field(
        ...,
        description="A list of observation deletions, each specifying an entity and observations to remove",
    )


class DeleteEntitiesRequest(BaseModel):
    entityNames: List[str] = Field(
        ..., description="An array of entity names to delete"
    )


class DeleteRelationsRequest(BaseModel):
    relations: List[Relation] = Field(
        ..., description="An array of relations to delete"
    )


class SearchNodesRequest(BaseModel):
    query: str = Field(
        ...,
        description="The search query to match against entity names, types, and observation content",
    )


class OpenNodesRequest(BaseModel):
    names: List[str] = Field(..., description="An array of entity names to retrieve")
