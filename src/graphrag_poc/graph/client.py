"""Bolt driver for the local Neo4j Community instance."""

import os

from neo4j import Driver, GraphDatabase


def make_driver(
    uri: str | None = None,
    user: str | None = None,
    password: str | None = None,
) -> Driver:
    """Open a driver. Defaults match docker-compose.yml."""

    address = uri or os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    name = user or os.environ.get("NEO4J_USER", "neo4j")
    secret = password or os.environ.get("NEO4J_PASSWORD", "graphrag-poc")
    return GraphDatabase.driver(address, auth=(name, secret))
