"""
Bridge module for ingest_data functionality, re-exporting from ingestion_data.py
"""
from ingestion_data import ingest_data, chroma_client

__all__ = ["ingest_data", "chroma_client"]
