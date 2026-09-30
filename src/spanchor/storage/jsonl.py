"""JSONL storage for gold sets with schema validation.

This module provides line-by-line reading and writing of Query objects
in JSONL format (one JSON object per line), with strict schema validation
and duplicate detection.
"""

import json
from pathlib import Path

from spanchor.errors import InvalidSchemaError
from spanchor.models.anchor import Anchor
from spanchor.models.query import Query


def read_gold_set(path: Path) -> list[Query]:
    """Read JSONL gold set with line-by-line parsing and validation.

    Reads a JSONL file where each line contains a Query object as JSON.
    Validates schema_version and detects duplicate query_id values.

    Args:
        path: Path to the JSONL file

    Returns:
        List of Query objects

    Raises:
        InvalidSchemaError: If JSON is malformed, schema is invalid,
            required fields are missing, or duplicate query_id is found.
            Error includes file path, line number, and field details.

    Examples:
        >>> gold_set = read_gold_set(Path("gold.jsonl"))
        >>> len(gold_set)
        5
        >>> gold_set[0].query_id
        'q1'
    """
    queries = []
    seen_ids: set[str] = set()

    try:
        with path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    raise InvalidSchemaError(
                        message=f"Invalid JSON: {e.msg}",
                        file_path=str(path),
                        line_number=line_num,
                    ) from e

                # Validate it's a dictionary
                if not isinstance(data, dict):
                    raise InvalidSchemaError(
                        message=f"Expected JSON object, got {type(data).__name__}",
                        file_path=str(path),
                        line_number=line_num,
                    )

                # Validate schema_version presence
                if "schema_version" not in data:
                    raise InvalidSchemaError(
                        message="Missing required field 'schema_version'",
                        file_path=str(path),
                        line_number=line_num,
                        field_name="schema_version",
                    )

                # Validate required fields
                required_fields = ["query_id", "question", "anchors"]
                for field in required_fields:
                    if field not in data:
                        raise InvalidSchemaError(
                            message=f"Missing required field '{field}'",
                            file_path=str(path),
                            line_number=line_num,
                            field_name=field,
                        )

                # Check for duplicate query_id
                query_id = data["query_id"]
                if not isinstance(query_id, str):
                    raise InvalidSchemaError(
                        message=f"Field 'query_id' must be a string, got {type(query_id).__name__}",
                        file_path=str(path),
                        line_number=line_num,
                        field_name="query_id",
                    )

                if query_id in seen_ids:
                    raise InvalidSchemaError(
                        message=f"Duplicate query_id: '{query_id}'",
                        file_path=str(path),
                        line_number=line_num,
                        field_name="query_id",
                    )
                seen_ids.add(query_id)

                # Validate question field
                if not isinstance(data["question"], str):
                    raise InvalidSchemaError(
                        message=(
                            f"Field 'question' must be a string, "
                            f"got {type(data['question']).__name__}"
                        ),
                        file_path=str(path),
                        line_number=line_num,
                        field_name="question",
                    )

                # Deserialize anchors from dict
                anchors_data = data["anchors"]
                if not isinstance(anchors_data, list):
                    raise InvalidSchemaError(
                        message=(
                            f"Field 'anchors' must be a list, " f"got {type(anchors_data).__name__}"
                        ),
                        file_path=str(path),
                        line_number=line_num,
                        field_name="anchors",
                    )

                try:
                    anchors = []
                    for anchor_idx, anchor_dict in enumerate(anchors_data):
                        if not isinstance(anchor_dict, dict):
                            raise InvalidSchemaError(
                                message=(
                                    f"Anchor at index {anchor_idx} must be a dict, "
                                    f"got {type(anchor_dict).__name__}"
                                ),
                                file_path=str(path),
                                line_number=line_num,
                                field_name=f"anchors[{anchor_idx}]",
                            )

                        # Validate anchor required fields
                        anchor_required = ["document_id", "start", "end", "expected_text_hash"]
                        for field in anchor_required:
                            if field not in anchor_dict:
                                raise InvalidSchemaError(
                                    message=f"Anchor at index {anchor_idx} missing field '{field}'",
                                    file_path=str(path),
                                    line_number=line_num,
                                    field_name=f"anchors[{anchor_idx}].{field}",
                                )

                        # Validate anchor field types
                        if not isinstance(anchor_dict["document_id"], str):
                            raise InvalidSchemaError(
                                message=(
                                    f"Anchor field 'document_id' must be string, "
                                    f"got {type(anchor_dict['document_id']).__name__}"
                                ),
                                file_path=str(path),
                                line_number=line_num,
                                field_name=f"anchors[{anchor_idx}].document_id",
                            )

                        if not isinstance(anchor_dict["start"], int):
                            raise InvalidSchemaError(
                                message=(
                                    f"Anchor field 'start' must be int, "
                                    f"got {type(anchor_dict['start']).__name__}"
                                ),
                                file_path=str(path),
                                line_number=line_num,
                                field_name=f"anchors[{anchor_idx}].start",
                            )

                        if not isinstance(anchor_dict["end"], int):
                            raise InvalidSchemaError(
                                message=(
                                    f"Anchor field 'end' must be int, "
                                    f"got {type(anchor_dict['end']).__name__}"
                                ),
                                file_path=str(path),
                                line_number=line_num,
                                field_name=f"anchors[{anchor_idx}].end",
                            )

                        if not isinstance(anchor_dict["expected_text_hash"], str):
                            raise InvalidSchemaError(
                                message=(
                                    f"Anchor field 'expected_text_hash' must be string, "
                                    f"got {type(anchor_dict['expected_text_hash']).__name__}"
                                ),
                                file_path=str(path),
                                line_number=line_num,
                                field_name=f"anchors[{anchor_idx}].expected_text_hash",
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

                except (TypeError, ValueError) as e:
                    raise InvalidSchemaError(
                        message=f"Error deserializing anchors: {e}",
                        file_path=str(path),
                        line_number=line_num,
                        field_name="anchors",
                    ) from e

                # Create Query object
                try:
                    query = Query(
                        query_id=query_id,
                        question=data["question"],
                        anchors=tuple(anchors),
                        schema_version=data["schema_version"],
                    )
                    queries.append(query)
                except (TypeError, ValueError) as e:
                    raise InvalidSchemaError(
                        message=f"Error creating Query object: {e}",
                        file_path=str(path),
                        line_number=line_num,
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

    return queries


def write_gold_set(path: Path, queries: list[Query]) -> None:
    """Write queries to JSONL format (one per line).

    Each query is serialized as JSON with all fields including schema_version,
    and Anchor objects are converted to dictionaries.

    Args:
        path: Path to the output JSONL file
        queries: List of Query objects to write

    Raises:
        InvalidSchemaError: If file cannot be written (permissions, disk space, etc.)

    Examples:
        >>> queries = [Query("q1", "What is X?", (), "0.1.0")]
        >>> write_gold_set(Path("output.jsonl"), queries)
    """
    try:
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as f:
            for query in queries:
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

                # Create query dict
                query_dict = {
                    "query_id": query.query_id,
                    "question": query.question,
                    "anchors": anchors_data,
                    "schema_version": query.schema_version,
                }

                # Write as single line
                json.dump(query_dict, f, ensure_ascii=False)
                f.write("\n")

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
