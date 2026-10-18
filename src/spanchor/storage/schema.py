"""Schema version constants and documentation for Run objects.

This module defines schema versions and provides documentation for
backward compatibility and migration strategies.
"""

# Schema version constants
SCHEMA_VERSION_V0_1_0 = "0.1.0"
"""Original schema version (baseline, no corpus_hash or gold_set_hash)."""

SCHEMA_VERSION_V0_2_0 = "0.2.0"
"""Current schema version (adds optional corpus_hash and gold_set_hash fields)."""

# Current active schema version (for all new writes)
SCHEMA_VERSION_CURRENT = SCHEMA_VERSION_V0_2_0

# Supported schema versions for reading
SUPPORTED_VERSIONS = {SCHEMA_VERSION_V0_1_0, SCHEMA_VERSION_V0_2_0}


class RunSchemaV0_1_0:
    """Schema documentation for Run v0.1.0 (original baseline).

    Fields:
        timestamp: ISO format timestamp
        queries: List of Query objects
        per_query_metrics: Dict[query_id -> Dict[metric_name -> float]]
        aggregate_metrics: Dict[metric_name -> float]
        config: Dict of configuration parameters
        mapper_stats: Dict of mapping status counts
        schema_version: "0.1.0"

    No corpus fingerprint fields.
    """

    pass


class RunSchemaV0_2_0:
    """Schema documentation for Run v0.2.0 (additive schema evolution).

    Fields:
        (All v0.1.0 fields, unchanged)
        timestamp: ISO format timestamp
        queries: List of Query objects
        per_query_metrics: Dict[query_id -> Dict[metric_name -> float]]
        aggregate_metrics: Dict[metric_name -> float]
        config: Dict of configuration parameters
        mapper_stats: Dict of mapping status counts
        schema_version: "0.2.0"

    NEW in v0.2.0 (optional, default None):
        corpus_hash: SHA256 fingerprint of corpus (str | None)
            - Computed from deterministic JSON representation of all documents
            - Identifies corpus structure and content
            - Used for mismatch detection
            - None for old runs (v0.1.0 migrations)

        gold_set_hash: SHA256 fingerprint of gold set structure (str | None)
            - Computed from canonical JSON of query anchor structure
            - Identifies gold set evaluation targets
            - Used for reproducibility and mismatch detection
            - None for old runs (v0.1.0 migrations)

    Migration Strategy:
        - read_run() auto-detects v0.1.0 and migrates to v0.2.0 in-memory
        - Missing corpus_hash/gold_set_hash fields are set to None
        - Deprecation warning emitted on migration
        - Old v0.1.0 Runs remain unchanged on disk
        - write_run() always writes v0.2.0 format

    Backward Compatibility:
        - New code can read both v0.1.0 and v0.2.0 Runs
        - Old v0.1.0 code cannot read v0.2.0 (corpus_hash/gold_set_hash are unexpected)
        - To restore v0.3.0 compatibility: run evaluation again (produces v0.2.0)
    """

    pass
