# Repository structure

src/spanchor/
  __init__.py            # public API: Anchor, evaluate, compare, check_corpus
  models/                # anchor, document, query, retrieval, run (dataclasses)
  canonical/             # normalize.py, hashing.py
  mapping/               # chunk-to-span mapper (v0.1, core)
  anchors/               # exact.py (v0.1); resolve.py, fuzzy.py (v0.2)
  evaluation/            # intervals.py, hit.py, recall.py, precision.py, iou.py
  comparison/            # compare.py, regression.py, warnings.py; statistics.py (v0.2)
  storage/               # jsonl.py, schema.py
  annotation/            # locate.py (v0.1 minimal helper); proposals.py (later)
  adapters/              # base.py (protocol); framework adapters later
  reporting/             # markdown.py, json.py, redaction.py
  cli.py, errors.py

tests/{unit,integration,regression,fixtures}
examples/demo/{docs,gold.jsonl,baseline.json,candidate.json}
benchmarks/
docs/
.github/workflows/{tests,lint,release}.yml
