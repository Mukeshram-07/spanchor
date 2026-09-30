"""Anchor add helper for creating gold set entries via CLI.

Provides add_anchor() to locate text in documents, create a validated
Anchor and Query, and append them to a gold JSONL file.
"""

from __future__ import annotations

import json
from pathlib import Path

from spanchor.annotation.locate import LocateMatch, locate_text
from spanchor.errors import InvalidSchemaError
from spanchor.models.anchor import Anchor
from spanchor.models.document import Document
from spanchor.models.query import Query


class AmbiguousTextError(Exception):
    """Raised when the search text matches multiple locations and no occurrence is specified.

    Attributes:
        match_count: Number of matches found
        matches: The list of LocateMatch objects
    """

    def __init__(self, match_count: int, matches: list[LocateMatch]) -> None:
        self.match_count = match_count
        self.matches = matches
        super().__init__(
            f"Text is ambiguous: found {match_count} occurrences. "
            f"Use --occurrence N (1-{match_count}) to select a specific occurrence.\n"
            "Suggested action: Re-run with --occurrence N to pick the desired match."
        )


class TextNotFoundError(Exception):
    """Raised when the search text is not found in any document."""

    def __init__(self, search_text: str) -> None:
        self.search_text = search_text
        preview = search_text[:60] + "..." if len(search_text) > 60 else search_text
        super().__init__(
            f"Text not found in any document: {preview!r}\n"
            "Suggested action: Check the text spelling and ensure documents are loaded."
        )


class OccurrenceOutOfRangeError(Exception):
    """Raised when the requested occurrence N is out of range.

    Attributes:
        requested: The occurrence number that was requested
        available: Total number of matches available
    """

    def __init__(self, requested: int, available: int) -> None:
        self.requested = requested
        self.available = available
        super().__init__(
            f"Occurrence {requested} is out of range: only {available} match(es) found. "
            f"Use --occurrence N where N is between 1 and {available}.\n"
            "Suggested action: Re-run with a valid --occurrence value."
        )


class DuplicateQueryIdError(Exception):
    """Raised when the query_id already exists in the gold file.

    Attributes:
        query_id: The duplicate query identifier
        gold_path: Path to the gold JSONL file
    """

    def __init__(self, query_id: str, gold_path: Path) -> None:
        self.query_id = query_id
        self.gold_path = gold_path
        super().__init__(
            f"query_id '{query_id}' already exists in '{gold_path}'.\n"
            "Suggested action: Choose a different query_id or use a different gold file."
        )


def _read_existing_query_ids(gold_path: Path) -> set[str]:
    """Read the set of query_id values from an existing gold JSONL file.

    Args:
        gold_path: Path to the JSONL file (must exist)

    Returns:
        Set of query_id strings found in the file

    Raises:
        InvalidSchemaError: If a line contains malformed JSON or is missing query_id
    """
    query_ids: set[str] = set()

    with gold_path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as exc:
                raise InvalidSchemaError(
                    message=f"Invalid JSON: {exc.msg}",
                    file_path=str(gold_path),
                    line_number=line_num,
                ) from exc

            if not isinstance(data, dict) or "query_id" not in data:
                raise InvalidSchemaError(
                    message="Missing required field 'query_id'",
                    file_path=str(gold_path),
                    line_number=line_num,
                    field_name="query_id",
                )

            query_ids.add(str(data["query_id"]))

    return query_ids


def _append_query_to_jsonl(gold_path: Path, query: Query) -> None:
    """Append a single Query to a JSONL file as a new line.

    Creates the file (and parent directories) if they do not exist.

    Args:
        gold_path: Destination JSONL file path
        query: Query object to serialize and append
    """
    gold_path.parent.mkdir(parents=True, exist_ok=True)

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

    query_dict = {
        "query_id": query.query_id,
        "question": query.question,
        "anchors": anchors_data,
        "schema_version": query.schema_version,
    }

    with gold_path.open("a", encoding="utf-8") as f:
        json.dump(query_dict, f, ensure_ascii=False)
        f.write("\n")


def add_anchor(
    query_id: str,
    question: str,
    search_text: str,
    documents: dict[str, Document],
    gold_path: Path,
    occurrence: int | None = None,
) -> tuple[Query, LocateMatch]:
    """Locate text in documents, create a validated anchor, and append to the gold file.

    Workflow:
    1. Validate query_id uniqueness against the gold file (if it exists).
    2. Locate *search_text* in *documents* via locate_text().
    3. If text is unique (1 match), use that match.
    4. If text is ambiguous (>1 matches) and *occurrence* is None → raise AmbiguousTextError.
    5. If *occurrence* is given, pick that 1-based occurrence.
    6. Construct an Anchor from the chosen LocateMatch.
    7. Construct a Query wrapping the anchor.
    8. Create gold file if it doesn't exist; append the Query as a JSONL line.

    Args:
        query_id: Unique identifier for the new query entry
        question: Question text associated with the anchor
        search_text: Text to locate in documents; used verbatim then whitespace-normalized
        documents: Mapping of document_id → Document to search
        gold_path: Path to the gold JSONL file (created if absent)
        occurrence: 1-based index selecting which occurrence to use when multiple exist.
            Pass None to auto-select only when a single match is found.

    Returns:
        Tuple of (Query, LocateMatch) for the newly added entry, so callers can
        print confirmation details.

    Raises:
        TextNotFoundError: If *search_text* is not found in any document.
        AmbiguousTextError: If multiple matches exist and *occurrence* is None.
        OccurrenceOutOfRangeError: If *occurrence* is outside [1, len(matches)].
        DuplicateQueryIdError: If *query_id* already exists in the gold file.
        InvalidSchemaError: If the gold file exists but has malformed content.
    """
    # Req 16.7 – validate query_id uniqueness before adding
    if gold_path.exists():
        existing_ids = _read_existing_query_ids(gold_path)
        if query_id in existing_ids:
            raise DuplicateQueryIdError(query_id, gold_path)

    # Req 16.1 – locate text in documents
    matches = locate_text(search_text, documents)

    if not matches:
        raise TextNotFoundError(search_text)

    # Req 16.3 / 16.4 – handle ambiguity
    if len(matches) > 1 and occurrence is None:
        raise AmbiguousTextError(match_count=len(matches), matches=matches)

    if occurrence is not None:
        # Req 16.4 – use the Nth occurrence
        if occurrence < 1 or occurrence > len(matches):
            raise OccurrenceOutOfRangeError(requested=occurrence, available=len(matches))
        chosen: LocateMatch = matches[occurrence - 1]
    else:
        # Exactly one match, unique case (Req 16.2)
        chosen = matches[0]

    # Build Anchor from the chosen match
    anchor = Anchor(
        document_id=chosen.document_id,
        start=chosen.start,
        end=chosen.end,
        expected_text_hash=chosen.text_hash,
    )

    # Build Query wrapping the anchor
    query = Query(
        query_id=query_id,
        question=question,
        anchors=(anchor,),
    )

    # Req 16.6 – create gold file if it doesn't exist; Req 16.2 – append entry
    _append_query_to_jsonl(gold_path, query)

    return query, chosen
