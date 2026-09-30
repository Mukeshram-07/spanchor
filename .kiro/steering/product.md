# Product: spanchor

spanchor is a Python library + CLI for regression-testing RAG retrieval pipelines using stable source-document anchors instead of fragile chunk IDs.

Core principle: separate SOURCE EVIDENCE from RETRIEVAL REPRESENTATION. Gold labels point at character spans in canonical source documents. Any retriever output (spans OR chunk text) is mapped back to those spans and scored.

Central workflow: change retrieval pipeline -> run same gold set -> compare candidate vs baseline -> per-query regressions -> PASS/FAIL for CI.

NOT in scope: RAG framework, vector DB, embeddings, LLM provider, document parser, PDF/OCR, dashboards, agents, answer evaluation, multimodal (schema-extensible only).

Non-negotiables:
- Deterministic, local-first, no network calls, no telemetry, no API keys in core.
- Never silently move or repair an anchor; every resolution records its method/status.
- Never log source text by default; support redacted reports.
- Honest limitations: gold labels may be wrong; significance != practical significance.
