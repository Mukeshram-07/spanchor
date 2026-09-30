"""Regression policy model for configurable comparison thresholds.

A RegressionPolicy bundles per-metric max_drop thresholds with an optional
minimum-query-count guard. Policies can be loaded from JSON/YAML config files
and merged with CLI flag overrides.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RegressionPolicy:
    """Configurable thresholds for regression detection.

    Attributes:
        thresholds: Per-metric maximum allowed drop before a query is classified
            as REGRESSION.  Keys are metric names (e.g. ``"recall@5"``), values
            are non-negative floats.
            Example: ``{"recall@5": 0.05, "hit@5": 0.10}``

        min_query_count: Optional minimum number of common queries required for
            a comparison to be considered statistically meaningful.  When set,
            ``compare()`` will raise ``ComparisonError`` if the gold set has
            fewer common queries than this value.
    """

    thresholds: dict[str, float] = field(default_factory=dict)
    min_query_count: int | None = None

    def to_policy_dict(self) -> dict[str, float]:
        """Return the thresholds dict suitable for passing to compare().

        Returns:
            A copy of ``self.thresholds``.
        """
        return dict(self.thresholds)


def load_policy(path: Path | str) -> RegressionPolicy:
    """Load a RegressionPolicy from a JSON or YAML config file.

    The file must be valid JSON (or YAML, if PyYAML is installed) with an
    object at the top level.  Recognised top-level keys:

    * ``thresholds`` (dict[str, float]) — per-metric max_drop values.
      Individual metric keys may also be placed directly at the top level for
      convenience; they are folded into ``thresholds`` automatically if they
      are not one of the reserved keys.
    * ``min_query_count`` (int) — optional minimum-query-count guard.

    Examples of valid JSON files::

        {
            "thresholds": {
                "recall@5": 0.05,
                "hit@5": 0.10
            },
            "min_query_count": 20
        }

        {
            "recall@5": 0.05,
            "hit@5": 0.10,
            "min_query_count": 20
        }

    Args:
        path: Path to the policy config file (.json or .yaml/.yml).

    Returns:
        A populated ``RegressionPolicy`` instance.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file cannot be parsed or contains invalid values.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Policy file not found: {path}\n"
            "Suggested action: Check the path and create a policy JSON/YAML file."
        )

    raw: Any
    suffix = path.suffix.lower()

    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "PyYAML is required to load YAML policy files. "
                "Install it with: pip install pyyaml"
            ) from exc
        with path.open("r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
    else:
        # Default: treat as JSON
        try:
            with path.open("r", encoding="utf-8") as fh:
                raw = json.load(fh)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Failed to parse policy file as JSON: {path}\n"
                f"Error: {exc}\n"
                "Suggested action: Validate the JSON syntax and retry."
            ) from exc

    if not isinstance(raw, dict):
        raise ValueError(
            f"Policy file must contain a JSON/YAML object at the top level, "
            f"got {type(raw).__name__}: {path}"
        )

    return _parse_policy_dict(raw, source=str(path))


def merge_policy(
    base: RegressionPolicy,
    overrides: dict[str, Any],
) -> RegressionPolicy:
    """Merge CLI flag overrides into a base policy, returning a new policy.

    CLI overrides take precedence over values loaded from a config file.
    Only keys present in ``overrides`` (with non-None values) are applied;
    absent or None-valued keys leave the base untouched.

    Recognised override keys:

    * Any metric name (e.g. ``"recall@5"``) with a float value — updates
      ``thresholds[metric]``.
    * ``"min_query_count"`` with an int value — updates ``min_query_count``.
    * ``"thresholds"`` with a dict value — merges the entire thresholds dict.

    Args:
        base: The base ``RegressionPolicy`` loaded from a config file (or a
            default empty policy).
        overrides: Flat dict of CLI-derived values.  None values are ignored.
            Example: ``{"recall@5": 0.03, "min_query_count": 50}``

    Returns:
        A new ``RegressionPolicy`` with overrides applied.

    Example::

        base = load_policy("policy.json")
        cli_overrides = {"recall@5": 0.03, "min_query_count": None}
        merged = merge_policy(base, cli_overrides)
        # recall@5 is now 0.03; min_query_count unchanged from base
    """
    new_thresholds = dict(base.thresholds)
    new_min_query_count = base.min_query_count

    for key, value in overrides.items():
        if value is None:
            # Explicit None → leave base value intact
            continue

        if key == "min_query_count":
            if not isinstance(value, int):
                raise ValueError(
                    f"min_query_count override must be an integer, got {type(value).__name__}: {value!r}"
                )
            new_min_query_count = value
        elif key == "thresholds":
            if not isinstance(value, dict):
                raise ValueError(f"thresholds override must be a dict, got {type(value).__name__}")
            for metric, threshold in value.items():
                _validate_threshold(metric, threshold)
                new_thresholds[metric] = float(threshold)
        else:
            # Treat any other key as a metric threshold
            _validate_threshold(key, value)
            new_thresholds[key] = float(value)

    return RegressionPolicy(
        thresholds=new_thresholds,
        min_query_count=new_min_query_count,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_RESERVED_KEYS = {"thresholds", "min_query_count"}


def _parse_policy_dict(data: dict[str, Any], source: str = "<dict>") -> RegressionPolicy:
    """Parse a raw dict into a RegressionPolicy.

    Handles both nested (``{"thresholds": {...}}`` style) and flat
    (individual metric keys at top level) formats.
    """
    thresholds: dict[str, float] = {}
    min_query_count: int | None = None

    # --- Nested thresholds block ---
    if "thresholds" in data:
        raw_thresholds = data["thresholds"]
        if not isinstance(raw_thresholds, dict):
            raise ValueError(
                f"'thresholds' in policy file must be a dict, "
                f"got {type(raw_thresholds).__name__}: {source}"
            )
        for metric, value in raw_thresholds.items():
            _validate_threshold(metric, value, source=source)
            thresholds[metric] = float(value)

    # --- min_query_count ---
    if "min_query_count" in data:
        mqc = data["min_query_count"]
        if not isinstance(mqc, int):
            raise ValueError(
                f"'min_query_count' must be an integer, got {type(mqc).__name__}: {source}"
            )
        if mqc < 0:
            raise ValueError(f"'min_query_count' must be non-negative, got {mqc}: {source}")
        min_query_count = mqc

    # --- Flat metric keys (convenience format) ---
    for key, value in data.items():
        if key in _RESERVED_KEYS:
            continue
        # Anything else is treated as a metric threshold
        _validate_threshold(key, value, source=source)
        thresholds[key] = float(value)

    return RegressionPolicy(thresholds=thresholds, min_query_count=min_query_count)


def _validate_threshold(metric: str, value: Any, source: str = "<dict>") -> None:
    """Raise ValueError if a threshold value is not a valid non-negative number."""
    if not isinstance(value, (int, float)):
        raise ValueError(
            f"Threshold for metric '{metric}' must be a number, "
            f"got {type(value).__name__}: {value!r}  [{source}]"
        )
    if float(value) < 0:
        raise ValueError(
            f"Threshold for metric '{metric}' must be non-negative, " f"got {value}  [{source}]"
        )
