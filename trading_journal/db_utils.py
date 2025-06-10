"""Utilities for initializing and querying DuckDB."""

import duckdb

DB_PATH = 'journal.duckdb'


def init_db(db_path: str = DB_PATH) -> duckdb.DuckDBPyConnection:
    """Initialize a DuckDB database and return a connection."""
    conn = duckdb.connect(db_path)
    return conn


def query_db(query: str, params=None, db_path: str = DB_PATH):
    """Execute a query against the DuckDB database."""
    if params is None:
        params = []
    with duckdb.connect(db_path) as conn:
        return conn.execute(query, params).fetchall()
