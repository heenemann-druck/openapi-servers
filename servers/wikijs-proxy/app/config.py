"""Configuration from environment."""
import os

WIKIJS_URL = os.environ.get("WIKIJS_URL", "http://wikijs:3000").rstrip("/")
WIKIJS_API_KEY = os.environ.get("WIKIJS_API_KEY", "")
GRAPHQL_URL = f"{WIKIJS_URL}/graphql"
