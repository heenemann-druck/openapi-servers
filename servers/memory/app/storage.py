"""Persistence: read/save knowledge graph from file."""
import json
import os
from pathlib import Path

from app.schemas import Entity, KnowledgeGraph, Relation

MEMORY_FILE_PATH_ENV = os.getenv("MEMORY_FILE_PATH", "memory.json")
MEMORY_FILE_PATH = Path(
    MEMORY_FILE_PATH_ENV
    if Path(MEMORY_FILE_PATH_ENV).is_absolute()
    else Path(__file__).resolve().parent.parent / MEMORY_FILE_PATH_ENV
)


def read_graph_file() -> KnowledgeGraph:
    if not MEMORY_FILE_PATH.exists():
        return KnowledgeGraph(entities=[], relations=[])
    with open(MEMORY_FILE_PATH, "r", encoding="utf-8") as f:
        lines = [line for line in f if line.strip()]
        entities = []
        relations = []
        for line in lines:
            item = json.loads(line)
            if item["type"] == "entity":
                entities.append(
                    Entity(
                        name=item["name"],
                        entityType=item["entityType"],
                        observations=item["observations"],
                    )
                )
            elif item["type"] == "relation":
                relations.append(Relation(**item))
        return KnowledgeGraph(entities=entities, relations=relations)


def save_graph(graph: KnowledgeGraph) -> None:
    lines = [json.dumps({"type": "entity", **e.dict()}) for e in graph.entities] + [
        json.dumps({"type": "relation", **r.dict(by_alias=True)})
        for r in graph.relations
    ]
    with open(MEMORY_FILE_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
