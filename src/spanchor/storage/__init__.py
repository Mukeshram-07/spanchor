"""Storage layer for JSONL and JSON serialization.

Handles reading and writing gold sets, runs, and other data with
strict schema validation.
"""

from spanchor.storage.json_io import read_run, write_run
from spanchor.storage.jsonl import read_gold_set, write_gold_set

__all__ = ["read_gold_set", "write_gold_set", "read_run", "write_run"]
