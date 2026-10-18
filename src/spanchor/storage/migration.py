"""Migration logic for backward compatibility across schema versions.

This module provides functions to migrate Run objects from v0.1.0 to v0.2.0
and handle forward/backward compatibility checks.
"""

import warnings

from spanchor.models.run import Run
from spanchor.storage.schema import SCHEMA_VERSION_V0_1_0, SCHEMA_VERSION_V0_2_0


def migrate_run_0_1_0_to_0_2_0(run: Run) -> Run:
    """Migrate a v0.1.0 Run to v0.2.0 schema.

    The migration adds optional fields (corpus_hash, gold_set_hash) with None
    defaults. All other fields are preserved unchanged.

    Args:
        run: Run object with schema_version "0.1.0"

    Returns:
        New Run object with:
        - schema_version: "0.2.0"
        - corpus_hash: None (not computed from v0.1.0)
        - gold_set_hash: None (not computed from v0.1.0)
        - All other fields unchanged

    Raises:
        ValueError: If run.schema_version is not "0.1.0"
    """
    if run.schema_version != SCHEMA_VERSION_V0_1_0:
        msg = (
            f"Cannot migrate from schema version {run.schema_version}. "
            f"Expected {SCHEMA_VERSION_V0_1_0}"
        )
        raise ValueError(msg)

    # Emit deprecation warning
    warnings.warn(
        "Migrating Run from schema v0.1.0 to v0.2.0. "
        "Re-run evaluation to populate corpus_hash and gold_set_hash.",
        DeprecationWarning,
        stacklevel=3,
    )

    # Create new Run with v0.2.0 schema
    migrated = Run(
        timestamp=run.timestamp,
        queries=run.queries,
        per_query_metrics=run.per_query_metrics,
        aggregate_metrics=run.aggregate_metrics,
        config=run.config,
        mapper_stats=run.mapper_stats,
        schema_version=SCHEMA_VERSION_V0_2_0,
        corpus_hash=None,
        gold_set_hash=None,
    )

    return migrated


def apply_migrations(run: Run) -> Run:
    """Apply all necessary migrations to bring a Run to current schema version.

    This function detects the Run's current schema version and applies
    appropriate migrations to reach the current active schema.

    Args:
        run: Run object with any schema_version

    Returns:
        Run object at current schema version with all fields populated

    Raises:
        ValueError: If run.schema_version is not supported

    Warnings:
        DeprecationWarning: If migration was applied (v0.1.0 detected)
    """
    current_version = SCHEMA_VERSION_V0_2_0

    if run.schema_version == current_version:
        # Already at current version, no migration needed
        return run

    if run.schema_version == SCHEMA_VERSION_V0_1_0:
        # Migrate v0.1.0 -> v0.2.0
        return migrate_run_0_1_0_to_0_2_0(run)

    # Unsupported version
    msg = f"Unsupported schema version: {run.schema_version}. Supported: 0.1.0, 0.2.0"
    raise ValueError(msg)
