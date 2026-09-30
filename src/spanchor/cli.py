"""CLI entry point for spanchor using Typer + Rich.

Commands:
    validate     – Validate gold set anchors against source documents.
    evaluate     – Evaluate retrieval results against gold anchors.
    compare      – Compare two evaluation runs for regressions.
    locate       – Find text across documents and display matches with offsets/context.
    anchor       – Manage gold set anchors (subcommands: add).
    check-corpus – Verify document corpus health.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from spanchor.annotation.locate import format_matches, locate_text
from spanchor.errors import ComparisonError, DocumentNotFoundError, EvaluationError, SpanchorError
from spanchor.models.document import Document
from spanchor.models.retrieval import RetrievalResult
from spanchor.storage.jsonl import read_gold_set

app = typer.Typer(
    name="spanchor",
    help="Regression-testing for RAG retrieval pipelines using stable source-document anchors.",
    add_completion=False,
)

# ---------------------------------------------------------------------------
# anchor sub-application
# ---------------------------------------------------------------------------

anchor_app = typer.Typer(
    name="anchor",
    help="Manage anchors in the gold set.",
    add_completion=False,
)
app.add_typer(anchor_app, name="anchor")

console = Console()
err_console = Console(stderr=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_documents(docs_dir: Path) -> dict[str, Document]:
    """Load and canonicalize all documents from a directory.

    Each file in the directory becomes a Document.  The document_id is the
    filename **without** its extension (e.g. ``report.txt`` → ``"report"``).
    Files are read as UTF-8 text.  Non-file entries (sub-directories, symlinks
    to non-files) are silently skipped.

    Args:
        docs_dir: Directory containing source document files.

    Returns:
        Mapping of document_id → :class:`~spanchor.models.document.Document`.

    Raises:
        :class:`typer.BadParameter`: If *docs_dir* is not an existing directory.
        :class:`spanchor.errors.InvalidSchemaError`: If any file cannot be read as UTF-8.
    """
    if not docs_dir.is_dir():
        raise typer.BadParameter(
            f"'{docs_dir}' is not a directory or does not exist.",
            param_hint="docs_dir",
        )

    documents: dict[str, Document] = {}

    for entry in sorted(docs_dir.iterdir()):
        if not entry.is_file():
            continue  # skip sub-directories

        document_id = entry.stem  # filename without extension
        raw_text = entry.read_text(encoding="utf-8")
        documents[document_id] = Document.from_text(document_id, raw_text)

    return documents


# ---------------------------------------------------------------------------
# validate command
# ---------------------------------------------------------------------------


@app.command()
def validate(
    docs_dir: Path = typer.Argument(
        ...,
        help="Directory containing source document files (one file per document).",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    gold_path: Path = typer.Argument(
        ...,
        help="Path to the gold set JSONL file.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
) -> None:
    """Validate every anchor in the gold set against its source document.

    Loads and canonicalizes all documents from DOCS_DIR, parses the gold set
    from GOLD_PATH, then validates every anchor against its referenced document.

    Exits with code 0 on success, code 2 on any validation error.

    Requirements: 17.1, 17.2, 17.3, 17.4, 17.5
    """
    errors: list[str] = []

    # Req 17.1 – load and canonicalize all documents
    try:
        documents = load_documents(docs_dir)
    except (typer.BadParameter, SpanchorError) as exc:
        err_console.print(f"[red]Error loading documents: {exc}[/red]")
        raise typer.Exit(2) from exc

    # Req 17.2 – load and parse the gold set
    try:
        queries = read_gold_set(gold_path)
    except SpanchorError as exc:
        err_console.print(f"[red]Error loading gold set: {exc}[/red]")
        raise typer.Exit(2) from exc

    # Req 17.3 – validate every anchor against its referenced document
    total_anchors = 0
    for query in queries:
        for anchor in query.anchors:
            total_anchors += 1
            doc = documents.get(anchor.document_id)
            if doc is None:
                errors.append(str(DocumentNotFoundError(anchor.document_id, query.query_id)))
                continue
            try:
                anchor.validate(doc)
            except SpanchorError as exc:
                errors.append(str(exc))

    # Req 17.5 – print all errors and exit code 2 on failure
    if errors:
        err_console.print(f"[red]Validation failed with {len(errors)} error(s):[/red]\n")
        for i, error_msg in enumerate(errors, start=1):
            err_console.print(f"[red][{i}] {error_msg}[/red]\n")
        raise typer.Exit(2)

    # Req 17.4 – print success message with counts
    console.print(
        f"[green]✓ Validated {len(documents)} document(s), "
        f"{len(queries)} quer{'y' if len(queries) == 1 else 'ies'}, "
        f"{total_anchors} anchor(s)[/green]"
    )
    raise typer.Exit(0)


# ---------------------------------------------------------------------------
# evaluate command
# ---------------------------------------------------------------------------


def _load_retrieval_results(results_path: Path) -> dict[str, list[RetrievalResult]]:
    """Load retrieval results from a JSON file.

    Supports two formats:
    - A JSON object mapping query_id → list of result dicts
    - Each result dict may have: rank, score, document_id, start, end, text

    Args:
        results_path: Path to the JSON results file.

    Returns:
        Mapping of query_id → list of :class:`~spanchor.models.retrieval.RetrievalResult`.

    Raises:
        :class:`spanchor.errors.InvalidSchemaError`: If the file is malformed.
    """
    from spanchor.errors import InvalidSchemaError

    try:
        with results_path.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as exc:
                raise InvalidSchemaError(
                    message=f"Invalid JSON: {exc.msg}",
                    file_path=str(results_path),
                    line_number=exc.lineno,
                ) from exc
    except FileNotFoundError:
        raise InvalidSchemaError(
            message=f"File not found: {results_path}",
            file_path=str(results_path),
        ) from None
    except PermissionError:
        raise InvalidSchemaError(
            message=f"Permission denied: {results_path}",
            file_path=str(results_path),
        ) from None

    if not isinstance(data, dict):
        from spanchor.errors import InvalidSchemaError as ISE

        raise ISE(
            message=f"Expected JSON object mapping query_id → results, got {type(data).__name__}",
            file_path=str(results_path),
        )

    retrieval_results: dict[str, list[RetrievalResult]] = {}

    for query_id, raw_results in data.items():
        if not isinstance(raw_results, list):
            from spanchor.errors import InvalidSchemaError as ISE2

            raise ISE2(
                message=f"Results for query '{query_id}' must be a list, got {type(raw_results).__name__}",
                file_path=str(results_path),
                field_name=query_id,
            )

        results: list[RetrievalResult] = []
        for i, item in enumerate(raw_results):
            if not isinstance(item, dict):
                from spanchor.errors import InvalidSchemaError as ISE3

                raise ISE3(
                    message=f"Result at index {i} for query '{query_id}' must be a dict",
                    file_path=str(results_path),
                    field_name=f"{query_id}[{i}]",
                )

            rank = item.get("rank", i + 1)
            score = float(item.get("score", 0.0))
            document_id: str | None = item.get("document_id")
            start: int | None = item.get("start")
            end: int | None = item.get("end")
            text: str | None = item.get("text")

            results.append(
                RetrievalResult(
                    rank=int(rank),
                    score=score,
                    document_id=document_id,
                    start=int(start) if start is not None else None,
                    end=int(end) if end is not None else None,
                    text=text,
                )
            )

        retrieval_results[query_id] = results

    return retrieval_results


@app.command()
def evaluate(
    docs_dir: Path = typer.Argument(
        ...,
        help="Directory containing source document files (one file per document).",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    gold_path: Path = typer.Argument(
        ...,
        help="Path to the gold set JSONL file.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    results_path: Path = typer.Argument(
        ...,
        help="Path to the retrieval results JSON file (query_id → list of results).",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Write the Run object to this JSON file.",
    ),
    report: Optional[Path] = typer.Option(
        None,
        "--report",
        "-r",
        help="Write a markdown evaluation report to this file.",
    ),
    redact: bool = typer.Option(
        False,
        "--redact",
        help="Omit source text (query questions) from reports.",
    ),
    k: int = typer.Option(
        5,
        "--k",
        help="K value for Recall@K, Precision@K, Hit@K, FullEvidence@K.",
    ),
    max_unmapped_rate: float = typer.Option(
        0.1,
        "--max-unmapped-rate",
        help="Maximum allowed unmapped chunk rate (0.0–1.0). Exit code 3 if exceeded.",
    ),
) -> None:
    """Evaluate retrieval results against gold anchors.

    Loads documents from DOCS_DIR, gold anchors from GOLD_PATH, and retrieval
    results from RESULTS_PATH, then computes Recall@K, Precision@K, Hit@K,
    FullEvidence@K and IoU metrics.

    Exits with code 0 on success, code 3 when the unmapped chunk rate exceeds
    --max-unmapped-rate, and code 2 on schema/usage errors.

    Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7, 13.7, 13.8
    """
    # Req 18.1 / 13.8 – load documents
    try:
        documents = load_documents(docs_dir)
    except (typer.BadParameter, SpanchorError) as exc:
        err_console.print(f"[red]Error loading documents: {exc}[/red]")
        raise typer.Exit(2) from exc

    # Req 18.1 / 13.8 – load gold set
    try:
        queries = read_gold_set(gold_path)
    except SpanchorError as exc:
        err_console.print(f"[red]Error loading gold set: {exc}[/red]")
        raise typer.Exit(2) from exc

    # Req 18.1 / 18.2 / 13.8 – load retrieval results
    try:
        retrieval_results = _load_retrieval_results(results_path)
    except SpanchorError as exc:
        err_console.print(f"[red]Error loading retrieval results: {exc}[/red]")
        raise typer.Exit(2) from exc

    # Req 18.1, 18.2, 18.3 – run evaluation
    import warnings

    from spanchor.evaluation.engine import evaluate as run_evaluate

    try:
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            run = run_evaluate(
                documents=documents,
                queries=queries,
                retrieval_results=retrieval_results,
                k=k,
                max_unmapped_rate=max_unmapped_rate,
            )

        # Surface any UserWarnings (e.g. small gold-set warning)
        for w in caught_warnings:
            err_console.print(f"[yellow]Warning: {w.message}[/yellow]")

    except EvaluationError as exc:
        msg = str(exc)
        # Req 13.7 – unmapped rate exceeded → exit 3
        if "unmapped" in msg.lower():
            err_console.print(f"[red]Unmapped rate exceeded: {exc}[/red]")
            raise typer.Exit(3) from exc
        # Req 13.8 – other evaluation errors → exit 2
        err_console.print(f"[red]Evaluation error: {exc}[/red]")
        raise typer.Exit(2) from exc
    except SpanchorError as exc:
        err_console.print(f"[red]Error during evaluation: {exc}[/red]")
        raise typer.Exit(2) from exc

    # Req 18.4 – write Run to JSON if --output given
    if output is not None:
        from spanchor.storage.json_io import write_run

        try:
            write_run(output, run, redact=redact)
            console.print(f"[green]✓ Run written to {output}[/green]")
        except SpanchorError as exc:
            err_console.print(f"[red]Error writing output: {exc}[/red]")
            raise typer.Exit(2) from exc

    # Req 18.5, 18.6 – write markdown report if --report given
    if report is not None:
        from spanchor.reporting.markdown import generate_evaluation_report

        try:
            md = generate_evaluation_report(run, redact=redact)
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(md, encoding="utf-8")
            console.print(f"[green]✓ Markdown report written to {report}[/green]")
        except SpanchorError as exc:
            err_console.print(f"[red]Error writing report: {exc}[/red]")
            raise typer.Exit(2) from exc

    # Req 18.3 – print aggregate metrics summary to stdout
    agg = run.aggregate_metrics
    console.print("\n[bold]Aggregate Metrics[/bold]")
    for metric_name, value in sorted(agg.items()):
        console.print(f"  {metric_name}: {value:.4f}")

    mapper_stats = run.mapper_stats
    total = sum(mapper_stats.values())
    unmapped = mapper_stats.get("UNMAPPED", 0)
    if total > 0:
        unmapped_rate = unmapped / total
        console.print(
            f"\n[bold]Mapper stats:[/bold] {total} chunk(s) processed, "
            f"unmapped rate: {unmapped_rate:.2%}"
        )

    # Req 18.7 – exit 0 on success
    console.print("\n[green]✓ Evaluation complete[/green]")
    raise typer.Exit(0)


# ---------------------------------------------------------------------------
# compare command
# ---------------------------------------------------------------------------


@app.command()
def compare(
    baseline_path: Path = typer.Argument(
        ...,
        help="Path to the baseline run JSON file.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    candidate_path: Path = typer.Argument(
        ...,
        help="Path to the candidate run JSON file.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    report: Optional[Path] = typer.Option(
        None,
        "--report",
        "-r",
        help="Write a markdown comparison report to this file.",
    ),
    policy: Optional[Path] = typer.Option(
        None,
        "--policy",
        help=(
            "Path to a JSON policy file with per-metric max_drop thresholds. "
            'Format: {"recall@5": 0.05, "precision@5": 0.05, "hit@5": 0.1}'
        ),
    ),
    max_recall_drop: Optional[float] = typer.Option(
        None,
        "--max-recall-drop",
        help="Maximum allowed drop for recall@5 (overrides policy file).",
    ),
    max_precision_drop: Optional[float] = typer.Option(
        None,
        "--max-precision-drop",
        help="Maximum allowed drop for precision@5 (overrides policy file).",
    ),
    redact: bool = typer.Option(
        False,
        "--redact",
        help="Omit source text (query questions) from comparison reports.",
    ),
) -> None:
    """Compare two evaluation runs and detect per-query regressions.

    Loads BASELINE_PATH and CANDIDATE_PATH run JSON files, computes per-query
    metric deltas, and classifies each query as IMPROVED, REGRESSION, or
    UNCHANGED using the configured policy thresholds.

    Exits with code 0 when all queries are UNCHANGED or IMPROVED, code 1 when
    any query shows a REGRESSION, and code 2 on schema/usage errors.

    Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7, 19.8, 19.9, 13.3, 13.4
    """
    from spanchor.comparison.compare import compare as run_compare
    from spanchor.storage.json_io import read_run

    # Req 19.1 – load both run files
    try:
        baseline_run = read_run(baseline_path)
    except SpanchorError as exc:
        err_console.print(f"[red]Error loading baseline run: {exc}[/red]")
        raise typer.Exit(2) from exc

    try:
        candidate_run = read_run(candidate_path)
    except SpanchorError as exc:
        err_console.print(f"[red]Error loading candidate run: {exc}[/red]")
        raise typer.Exit(2) from exc

    # Req 19.5 – build policy dict from --policy file
    policy_dict: dict[str, float] = {}
    if policy is not None:
        try:
            with policy.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
            if not isinstance(loaded, dict):
                err_console.print(
                    f"[red]Policy file must contain a JSON object, "
                    f"got {type(loaded).__name__}[/red]"
                )
                raise typer.Exit(2)
            for key, value in loaded.items():
                if not isinstance(key, str) or not isinstance(value, (int, float)):
                    err_console.print(
                        f"[red]Policy file keys must be strings and values must be "
                        f"numbers. Invalid entry: {key!r}: {value!r}[/red]"
                    )
                    raise typer.Exit(2)
            policy_dict = {k: float(v) for k, v in loaded.items()}
        except json.JSONDecodeError as exc:
            err_console.print(f"[red]Invalid JSON in policy file: {exc}[/red]")
            raise typer.Exit(2) from exc
        except (OSError, PermissionError) as exc:
            err_console.print(f"[red]Error reading policy file: {exc}[/red]")
            raise typer.Exit(2) from exc

    # Req 19.6 – CLI flags override policy file entries
    if max_recall_drop is not None:
        policy_dict["recall@5"] = max_recall_drop
    if max_precision_drop is not None:
        policy_dict["precision@5"] = max_precision_drop

    # Req 19.2, 19.3 – run comparison
    try:
        result = run_compare(
            baseline=baseline_run,
            candidate=candidate_run,
            policy=policy_dict,
        )
    except ComparisonError as exc:
        err_console.print(f"[red]Comparison error: {exc}[/red]")
        raise typer.Exit(2) from exc
    except SpanchorError as exc:
        err_console.print(f"[red]Error during comparison: {exc}[/red]")
        raise typer.Exit(2) from exc

    # Req 19.4, 19.9 – write markdown comparison report if --report given
    if report is not None:
        from spanchor.reporting.markdown import generate_comparison_report

        try:
            md = generate_comparison_report(
                comparison=result,
                baseline=baseline_run,
                candidate=candidate_run,
                redact=redact,
            )
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(md, encoding="utf-8")
            console.print(f"[green]✓ Comparison report written to {report}[/green]")
        except SpanchorError as exc:
            err_console.print(f"[red]Error writing report: {exc}[/red]")
            raise typer.Exit(2) from exc

    # Print aggregate delta summary to stdout
    agg_deltas = result.aggregate_deltas
    if agg_deltas:
        console.print("\n[bold]Aggregate Deltas[/bold]")
        for metric_name, delta in sorted(agg_deltas.items()):
            sign = "+" if delta >= 0 else ""
            console.print(f"  {metric_name}: {sign}{delta:.4f}")

    # Print per-query status summary
    improved = sum(1 for s in result.per_query_status.values() if s == "IMPROVED")
    regressed = sum(1 for s in result.per_query_status.values() if s == "REGRESSION")
    unchanged = sum(1 for s in result.per_query_status.values() if s == "UNCHANGED")
    total = len(result.per_query_status)

    console.print(
        f"\n[bold]Query Status:[/bold] {total} total — "
        f"[green]{improved} improved[/green], "
        f"[red]{regressed} regressed[/red], "
        f"{unchanged} unchanged"
    )

    # Req 13.3, 19.7 – any REGRESSION → exit code 1
    if result.has_regression:
        console.print("\n[red]✗ Regressions detected — exiting with code 1[/red]")

        # Print the regressed query details
        for qid, status in sorted(result.per_query_status.items()):
            if status == "REGRESSION":
                deltas = result.per_query_deltas.get(qid, {})
                details = ", ".join(
                    f"{m}: {'+' if d >= 0 else ''}{d:.4f}"
                    for m, d in sorted(deltas.items())
                    if m in policy_dict and d < -policy_dict[m]
                )
                console.print(f"  [red]{qid}[/red]: {details}")

        raise typer.Exit(1)

    # Req 13.4, 19.8 – all UNCHANGED or IMPROVED → exit code 0
    console.print("\n[green]✓ No regressions detected[/green]")
    raise typer.Exit(0)


# ---------------------------------------------------------------------------
# locate command
# ---------------------------------------------------------------------------


@app.command()
def locate(
    text: str = typer.Argument(
        ...,
        help="Text string to search for across documents.",
    ),
    docs_dir: Path = typer.Argument(
        ...,
        help="Directory containing source document files (one file per document).",
    ),
) -> None:
    """Find text in documents and display matching anchor candidates.

    Searches for TEXT across all documents in DOCS_DIR. First tries an exact
    match; if nothing is found, falls back to whitespace-normalized matching.
    Each match shows document_id, start/end offsets, text hash, and surrounding
    context so you can use the offsets to create gold anchors.

    Exits with code 0 on success (matches found or not), code 2 on error.

    Requirements: 15.1, 15.2, 15.3, 15.4, 15.5
    """
    # Req 15.1 – load documents from docs_dir
    try:
        documents = load_documents(docs_dir)
    except (typer.BadParameter, SpanchorError) as exc:
        err_console.print(f"[red]Error loading documents: {exc}[/red]")
        raise typer.Exit(2) from exc

    if not documents:
        err_console.print(f"[yellow]No documents found in '{docs_dir}'.[/yellow]")
        raise typer.Exit(0)

    # Req 15.1, 15.3 – search (exact first, then whitespace-normalized fallback)
    try:
        matches = locate_text(text, documents)
    except SpanchorError as exc:
        err_console.print(f"[red]Error during search: {exc}[/red]")
        raise typer.Exit(2) from exc

    # Req 15.2, 15.4, 15.5 – format and display results
    output = format_matches(matches)
    console.print(output)
    raise typer.Exit(0)


# ---------------------------------------------------------------------------
# anchor subcommands
# ---------------------------------------------------------------------------


@anchor_app.command("add")
def anchor_add(
    query_id: str = typer.Argument(
        ...,
        help="Unique identifier for the new gold query entry.",
    ),
    question: str = typer.Argument(
        ...,
        help="Question text associated with the anchor.",
    ),
    docs_dir: Path = typer.Argument(
        ...,
        help="Directory containing source document files (one file per document).",
    ),
    text: str = typer.Argument(
        ...,
        help="Text to locate in documents; used to create the anchor span.",
    ),
    gold: Path = typer.Option(
        Path("gold.jsonl"),
        "--gold",
        help="Path to the gold JSONL file (created if it does not exist).",
    ),
    occurrence: Optional[int] = typer.Option(
        None,
        "--occurrence",
        help=(
            "Select the Nth occurrence (1-based) when the text is found "
            "in multiple locations. Required when text is ambiguous."
        ),
    ),
) -> None:
    """Add a validated anchor to the gold JSONL file.

    Locates TEXT in documents under DOCS_DIR, creates an Anchor from the
    matched span, and appends a new Query entry to the gold file.

    When TEXT matches exactly one location the anchor is created automatically.
    When TEXT is ambiguous (multiple matches) you must pass --occurrence N.

    Exits with code 0 on success, code 2 on any error.

    Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7
    """
    from spanchor.annotation.add import (
        AmbiguousTextError,
        DuplicateQueryIdError,
        OccurrenceOutOfRangeError,
        TextNotFoundError,
        add_anchor,
    )
    from spanchor.annotation.locate import format_matches

    # Req 16.1 – load documents from docs_dir
    try:
        documents = load_documents(docs_dir)
    except (typer.BadParameter, SpanchorError) as exc:
        err_console.print(f"[red]Error loading documents: {exc}[/red]")
        raise typer.Exit(2) from exc

    if not documents:
        err_console.print(f"[yellow]No documents found in '{docs_dir}'.[/yellow]")
        raise typer.Exit(2)

    # Req 16.1, 16.2, 16.3, 16.4, 16.6, 16.7 – delegate to add_anchor()
    try:
        query, match = add_anchor(
            query_id=query_id,
            question=question,
            search_text=text,
            documents=documents,
            gold_path=gold,
            occurrence=occurrence,
        )
    except TextNotFoundError as exc:
        err_console.print(f"[red]Text not found: {exc}[/red]")
        raise typer.Exit(2) from exc
    except AmbiguousTextError as exc:
        # Req 16.3 – show occurrences so user knows which --occurrence to pick
        err_console.print(
            f"[yellow]Ambiguous text: found {exc.match_count} occurrences. "
            f"Use --occurrence N (1–{exc.match_count}) to select one.[/yellow]\n"
        )
        # Show first few matches for context (up to 5)
        preview_matches = exc.matches[:5]
        err_console.print(format_matches(preview_matches))
        if exc.match_count > 5:
            err_console.print(f"\n[dim]... and {exc.match_count - 5} more occurrences.[/dim]")
        raise typer.Exit(2) from exc
    except OccurrenceOutOfRangeError as exc:
        err_console.print(f"[red]Occurrence out of range: {exc}[/red]")
        raise typer.Exit(2) from exc
    except DuplicateQueryIdError as exc:
        err_console.print(f"[red]Duplicate query_id: {exc}[/red]")
        raise typer.Exit(2) from exc
    except SpanchorError as exc:
        err_console.print(f"[red]Error adding anchor: {exc}[/red]")
        raise typer.Exit(2) from exc

    # Req 16.5 – print confirmation with query_id and anchor details
    anchor = query.anchors[0]
    console.print("[green]✓ Anchor added successfully[/green]")
    console.print(f"  query_id    : {query.query_id}")
    console.print(f"  document_id : {anchor.document_id}")
    console.print(f"  offsets     : [{anchor.start}, {anchor.end})")
    console.print(f"  text_hash   : {anchor.expected_text_hash}")
    console.print(f"  gold file   : {gold}")
    raise typer.Exit(0)


# ---------------------------------------------------------------------------
# check-corpus command
# ---------------------------------------------------------------------------


@app.command("check-corpus")
def check_corpus_cmd(
    docs_dir: Path = typer.Argument(
        ...,
        help="Directory containing source document files (one file per document).",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    gold_path: Path = typer.Argument(
        ...,
        help="Path to the gold set JSONL file.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
) -> None:
    """Verify document corpus health by checking all anchors.

    Validates every anchor's document hash, offset bounds, and text match
    against documents in DOCS_DIR. Reports all issues with document_id and
    query_id.

    Exits with code 0 when corpus is healthy, code 2 when issues are found.

    Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6
    """
    from spanchor.validation import check_corpus

    # Load documents
    try:
        documents = load_documents(docs_dir)
    except (typer.BadParameter, SpanchorError) as exc:
        err_console.print(f"[red]Error loading documents: {exc}[/red]")
        raise typer.Exit(2) from exc

    # Load gold set
    try:
        queries = read_gold_set(gold_path)
    except SpanchorError as exc:
        err_console.print(f"[red]Error loading gold set: {exc}[/red]")
        raise typer.Exit(2) from exc

    # Req 20.1, 20.2, 20.3 – validate all anchors, collect all issues
    issues = check_corpus(documents, queries)

    total_anchors = sum(len(q.anchors) for q in queries)

    # Req 20.4, 20.6 – report issues and exit 2 if any found
    if issues:
        err_console.print(
            f"[red]Corpus check failed: {len(issues)} issue(s) found "
            f"across {len(queries)} quer{'y' if len(queries) == 1 else 'ies'} "
            f"({total_anchors} anchor(s) checked):[/red]\n"
        )
        for i, issue in enumerate(issues, start=1):
            err_console.print(
                f"[red][{i}] query_id={issue.query_id!r}, "
                f"document_id={issue.document_id!r}[/red]"
            )
            err_console.print(f"     {issue.message}\n")
        raise typer.Exit(2)

    # Req 20.5 – print success and exit 0 when healthy
    console.print(
        f"[green]✓ Corpus healthy: {len(documents)} document(s), "
        f"{len(queries)} quer{'y' if len(queries) == 1 else 'ies'}, "
        f"{total_anchors} anchor(s) checked — no issues found[/green]"
    )
    raise typer.Exit(0)
