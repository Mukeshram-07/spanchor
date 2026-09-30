"""JSON storage for runs with schema validation and redaction support.

This module provides read_run and write_run functions for Run objects
in JSON format, with strict schema validation and optional source text
redaction for privacy and size optimization.
"""

import json
from pathlib import Path

from spanchor.errors import InvalidSchemaError
from spanchor.models.anchor import Anchor
from spanchor.models.query import Query
from spanchor.models.run import Run


def read_run(path: Path) -> Run:
    """Read and validate Run from JSON file.

    Reads a JSON file containing a Run object and validates schema_version,
    required fields, and field types. Deserializes nested Query and Anchor
    objects.

    Args:
        path: Path to the JSON file

    Returns:
        Run object with all queries and metrics

    Raises:
        InvalidSchemaError: If JSON is malformed, schema is invalid,
            required fields are missing, or field types don't match.
            Error includes file path, field name, and suggested action.

    Examples:
        >>> run = read_run(Path("baseline.json"))
        >>> run.timestamp
        '2024-01-15T10:30:00Z'
        >>> len(run.queries)
        5
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise InvalidSchemaError(
                    message=f"Invalid JSON: {e.msg}",
                    file_path=str(path),
                    line_number=e.lineno,
                ) from e

    except FileNotFoundError:
        raise InvalidSchemaError(
            message=f"File not found: {path}",
            file_path=str(path),
        ) from None
    except PermissionError:
        raise InvalidSchemaError(
            message=f"Permission denied: {path}",
            file_path=str(path),
        ) from None

    # Validate it's a dictionary
    if not isinstance(data, dict):
        raise InvalidSchemaError(
            message=f"Expected JSON object, got {type(data).__name__}",
            file_path=str(path),
        )

    # Validate schema_version presence
    if "schema_version" not in data:
        raise InvalidSchemaError(
            message="Missing required field 'schema_version'",
            file_path=str(path),
            field_name="schema_version",
        )

    # Validate required fields
    required_fields = [
        "timestamp",
        "queries",
        "per_query_metrics",
        "aggregate_metrics",
        "config",
        "mapper_stats",
    ]
    for field in required_fields:
        if field not in data:
            raise InvalidSchemaError(
                message=f"Missing required field '{field}'",
                file_path=str(path),
                field_name=field,
            )

    # Validate field types
    if not isinstance(data["timestamp"], str):
        raise InvalidSchemaError(
            message=(
                f"Field 'timestamp' must be a string, " f"got {type(data['timestamp']).__name__}"
            ),
            file_path=str(path),
            field_name="timestamp",
        )

    if not isinstance(data["queries"], list):
        raise InvalidSchemaError(
            message=(f"Field 'queries' must be a list, " f"got {type(data['queries']).__name__}"),
            file_path=str(path),
            field_name="queries",
        )

    if not isinstance(data["per_query_metrics"], dict):
        raise InvalidSchemaError(
            message=(
                f"Field 'per_query_metrics' must be a dict, "
                f"got {type(data['per_query_metrics']).__name__}"
            ),
            file_path=str(path),
            field_name="per_query_metrics",
        )

    if not isinstance(data["aggregate_metrics"], dict):
        raise InvalidSchemaError(
            message=(
                f"Field 'aggregate_metrics' must be a dict, "
                f"got {type(data['aggregate_metrics']).__name__}"
            ),
            file_path=str(path),
            field_name="aggregate_metrics",
        )

    if not isinstance(data["config"], dict):
        raise InvalidSchemaError(
            message=(f"Field 'config' must be a dict, " f"got {type(data['config']).__name__}"),
            file_path=str(path),
            field_name="config",
        )

    if not isinstance(data["mapper_stats"], dict):
        raise InvalidSchemaError(
            message=(
                f"Field 'mapper_stats' must be a dict, "
                f"got {type(data['mapper_stats']).__name__}"
            ),
            file_path=str(path),
            field_name="mapper_stats",
        )

    # Deserialize queries
    try:
        queries = []
        for query_idx, query_dict in enumerate(data["queries"]):
            if not isinstance(query_dict, dict):
                raise InvalidSchemaError(
                    message=(
                        f"Query at index {query_idx} must be a dict, "
                        f"got {type(query_dict).__name__}"
                    ),
                    file_path=str(path),
                    field_name=f"queries[{query_idx}]",
                )

            # Validate query required fields
            query_required = ["query_id", "question", "anchors"]
            for field in query_required:
                if field not in query_dict:
                    raise InvalidSchemaError(
                        message=f"Query at index {query_idx} missing field '{field}'",
                        file_path=str(path),
                        field_name=f"queries[{query_idx}].{field}",
                    )

            # Validate query field types
            if not isinstance(query_dict["query_id"], str):
                raise InvalidSchemaError(
                    message=(
                        f"Query field 'query_id' must be string, "
                        f"got {type(query_dict['query_id']).__name__}"
                    ),
                    file_path=str(path),
                    field_name=f"queries[{query_idx}].query_id",
                )

            if not isinstance(query_dict["question"], str):
                raise InvalidSchemaError(
                    message=(
                        f"Query field 'question' must be string, "
                        f"got {type(query_dict['question']).__name__}"
                    ),
                    file_path=str(path),
                    field_name=f"queries[{query_idx}].question",
                )

            if not isinstance(query_dict["anchors"], list):
                raise InvalidSchemaError(
                    message=(
                        f"Query field 'anchors' must be list, "
                        f"got {type(query_dict['anchors']).__name__}"
                    ),
                    file_path=str(path),
                    field_name=f"queries[{query_idx}].anchors",
                )

            # Deserialize anchors
            anchors = []
            for anchor_idx, anchor_dict in enumerate(query_dict["anchors"]):
                if not isinstance(anchor_dict, dict):
                    raise InvalidSchemaError(
                        message=(
                            f"Anchor at index {anchor_idx} must be a dict, "
                            f"got {type(anchor_dict).__name__}"
                        ),
                        file_path=str(path),
                        field_name=f"queries[{query_idx}].anchors[{anchor_idx}]",
                    )

                # Validate anchor required fields
                anchor_required = ["document_id", "start", "end", "expected_text_hash"]
                for field in anchor_required:
                    if field not in anchor_dict:
                        raise InvalidSchemaError(
                            message=f"Anchor at index {anchor_idx} missing field '{field}'",
                            file_path=str(path),
                            field_name=f"queries[{query_idx}].anchors[{anchor_idx}].{field}",
                        )

                # Validate anchor field types
                if not isinstance(anchor_dict["document_id"], str):
                    raise InvalidSchemaError(
                        message=(
                            f"Anchor field 'document_id' must be string, "
                            f"got {type(anchor_dict['document_id']).__name__}"
                        ),
                        file_path=str(path),
                        field_name=f"queries[{query_idx}].anchors[{anchor_idx}].document_id",
                    )

                if not isinstance(anchor_dict["start"], int):
                    raise InvalidSchemaError(
                        message=(
                            f"Anchor field 'start' must be int, "
                            f"got {type(anchor_dict['start']).__name__}"
                        ),
                        file_path=str(path),
                        field_name=f"queries[{query_idx}].anchors[{anchor_idx}].start",
                    )

                if not isinstance(anchor_dict["end"], int):
                    raise InvalidSchemaError(
                        message=(
                            f"Anchor field 'end' must be int, "
                            f"got {type(anchor_dict['end']).__name__}"
                        ),
                        file_path=str(path),
                        field_name=f"queries[{query_idx}].anchors[{anchor_idx}].end",
                    )

                if not isinstance(anchor_dict["expected_text_hash"], str):
                    raise InvalidSchemaError(
                        message=(
                            f"Anchor field 'expected_text_hash' must be string, "
                            f"got {type(anchor_dict['expected_text_hash']).__name__}"
                        ),
                        file_path=str(path),
                        field_name=f"queries[{query_idx}].anchors[{anchor_idx}].expected_text_hash",
                    )

                # Create Anchor object
                anchor = Anchor(
                    document_id=anchor_dict["document_id"],
                    start=anchor_dict["start"],
                    end=anchor_dict["end"],
                    expected_text_hash=anchor_dict["expected_text_hash"],
                    schema_version=anchor_dict.get("schema_version", "0.1.0"),
                )
                anchors.append(anchor)

            # Create Query object
            query = Query(
                query_id=query_dict["query_id"],
                question=query_dict["question"],
                anchors=tuple(anchors),
                schema_version=query_dict.get("schema_version", "0.1.0"),
            )
            queries.append(query)

    except (TypeError, ValueError) as e:
        raise InvalidSchemaError(
            message=f"Error deserializing queries: {e}",
            file_path=str(path),
            field_name="queries",
        ) from e

    # Validate per_query_metrics structure
    for query_id, metrics in data["per_query_metrics"].items():
        if not isinstance(query_id, str):
            raise InvalidSchemaError(
                message=f"per_query_metrics key must be string, got {type(query_id).__name__}",
                file_path=str(path),
                field_name="per_query_metrics",
            )
        if not isinstance(metrics, dict):
            raise InvalidSchemaError(
                message=(
                    f"per_query_metrics['{query_id}'] must be dict, "
                    f"got {type(metrics).__name__}"
                ),
                file_path=str(path),
                field_name=f"per_query_metrics[{query_id}]",
            )
        for metric_name, value in metrics.items():
            if not isinstance(metric_name, str):
                raise InvalidSchemaError(
                    message=f"Metric name must be string, got {type(metric_name).__name__}",
                    file_path=str(path),
                    field_name=f"per_query_metrics[{query_id}]",
                )
            if not isinstance(value, (int, float)):
                raise InvalidSchemaError(
                    message=(
                        f"Metric value for '{metric_name}' must be numeric, "
                        f"got {type(value).__name__}"
                    ),
                    file_path=str(path),
                    field_name=f"per_query_metrics[{query_id}].{metric_name}",
                )

    # Validate aggregate_metrics structure
    for metric_name, value in data["aggregate_metrics"].items():
        if not isinstance(metric_name, str):
            raise InvalidSchemaError(
                message=f"Metric name must be string, got {type(metric_name).__name__}",
                file_path=str(path),
                field_name="aggregate_metrics",
            )
        if not isinstance(value, (int, float)):
            raise InvalidSchemaError(
                message=(
                    f"Metric value for '{metric_name}' must be numeric, "
                    f"got {type(value).__name__}"
                ),
                file_path=str(path),
                field_name=f"aggregate_metrics.{metric_name}",
            )

    # Validate mapper_stats structure
    for stat_name, count in data["mapper_stats"].items():
        if not isinstance(stat_name, str):
            raise InvalidSchemaError(
                message=f"Mapper stat name must be string, got {type(stat_name).__name__}",
                file_path=str(path),
                field_name="mapper_stats",
            )
        if not isinstance(count, int):
            raise InvalidSchemaError(
                message=(
                    f"Mapper stat count for '{stat_name}' must be int, "
                    f"got {type(count).__name__}"
                ),
                file_path=str(path),
                field_name=f"mapper_stats.{stat_name}",
            )

    # Create Run object
    try:
        run = Run(
            timestamp=data["timestamp"],
            queries=tuple(queries),
            per_query_metrics=data["per_query_metrics"],
            aggregate_metrics=data["aggregate_metrics"],
            config=data["config"],
            mapper_stats=data["mapper_stats"],
            schema_version=data["schema_version"],
        )
        return run
    except (TypeError, ValueError) as e:
        raise InvalidSchemaError(
            message=f"Error creating Run object: {e}",
            file_path=str(path),
        ) from e


def write_run(path: Path, run: Run, redact: bool = False) -> None:
    """Write Run to JSON format with optional redaction.

    Serializes a Run object to JSON format. When redaction is enabled,
    strips source text from queries (question field) for privacy and
    size optimization. All other fields including metrics, config, and
    mapper stats are preserved.

    Args:
        path: Path to the output JSON file
        run: Run object to write
        redact: If True, omit question text from queries (default: False)

    Raises:
        InvalidSchemaError: If file cannot be written (permissions, disk space, etc.)

    Examples:
        >>> run = Run(timestamp="2024-01-15T10:30:00Z", ...)
        >>> write_run(Path("output.json"), run)
        >>> write_run(Path("redacted.json"), run, redact=True)
    """
    try:
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Serialize queries
        queries_data = []
        for query in run.queries:
            # Serialize anchors to dict
            anchors_data = [
                {
                    "document_id": anchor.document_id,
                    "start": anchor.start,
                    "end": anchor.end,
                    "expected_text_hash": anchor.expected_text_hash,
                    "schema_version": anchor.schema_version,
                }
                for anchor in query.anchors
            ]

            # Create query dict with optional redaction
            query_dict = {
                "query_id": query.query_id,
                "question": "" if redact else query.question,
                "anchors": anchors_data,
                "schema_version": query.schema_version,
            }
            queries_data.append(query_dict)

        # Create run dict
        run_dict = {
            "timestamp": run.timestamp,
            "queries": queries_data,
            "per_query_metrics": run.per_query_metrics,
            "aggregate_metrics": run.aggregate_metrics,
            "config": run.config,
            "mapper_stats": run.mapper_stats,
            "schema_version": run.schema_version,
        }

        # Write to file
        with path.open("w", encoding="utf-8") as f:
            json.dump(run_dict, f, indent=2, ensure_ascii=False)

    except PermissionError:
        raise InvalidSchemaError(
            message=f"Permission denied writing to: {path}",
            file_path=str(path),
        ) from None
    except OSError as e:
        raise InvalidSchemaError(
            message=f"Error writing file: {e}",
            file_path=str(path),
        ) from e
