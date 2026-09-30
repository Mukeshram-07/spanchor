# SPANCHOR - Professional Description Optimization

**Version**: 0.1.0  
**Status**: Description-only optimization (no code changes)  
**Date**: 2026-09-30

---

## Current Description

### Short (PyPI)
```
Regression-testing for RAG retrieval pipelines using stable source-document anchors.
```

### Long (GitHub)
```
SPANCHOR is a Python library and CLI tool for regression-testing RAG retrieval systems.
Instead of relying on fragile chunk IDs, SPANCHOR anchors gold labels to character spans
in canonical source documents, then evaluates any retriever output against those stable anchors.
```

---

## RECOMMENDED DESCRIPTIONS

### 1. PyPI Short Description (80–120 chars)

**Recommended:**
```
Deterministic retrieval regression testing for RAG pipelines using source-document anchors.
```

**Why**: 
- Leads with the core differentiation: "source-document anchors"
- "Deterministic" emphasizes stability vs. fragile chunk IDs
- "Retrieval regression testing" is the primary use case
- Concise enough for PyPI discovery
- Contains strong keywords: retrieval, regression, testing, source

**Alternatives:**
```
Source-anchored evaluation for RAG retrieval regression testing.
```
(Shorter, direct, but less explicit about regression testing)

```
Stable-reference retrieval evaluation for RAG pipeline regression detection.
```
(More technical, might be clearer to experienced RAG engineers)

---

### 2. GitHub Repository Description

**Recommended:**
```
Deterministic retrieval evaluation for RAG pipelines.
Anchor gold evidence to source documents, evaluate retrieved results against
stable source anchors, detect retrieval regressions across pipeline changes.
```

**Why**:
- GitHub description can be 2–3 sentences
- First sentence is the hook
- Second sentence explains the workflow
- Third sentence clarifies the outcome
- Technically precise without jargon overload

---

### 3. README Opening Section

**Recommended:**

```markdown
# SPANCHOR

Test whether RAG retrieval systems return expected source evidence
when the retrieval pipeline changes.

## The Problem

RAG retrieval systems are fragile. When you change:
- chunk size or overlap
- retrieval algorithm or ranker
- document corpus
- indexing strategy

...your evaluation breaks because it's tied to generated chunk IDs or retrieval representation.

## The Solution

SPANCHOR separates source evidence from retrieval representation.

1. **Gold set**: Anchors point to character spans in canonical source documents
2. **Retrieve**: Any retriever (lexical, dense, hybrid) returns results
3. **Map**: Retrieved chunks are automatically mapped back to source spans
4. **Evaluate**: Metrics (Recall@K, Precision@K, Hit@K, IoU) measure evidence coverage
5. **Compare**: Baseline vs. candidate retrieval runs detect regressions
6. **Gate**: CI/CD exit codes (0=pass, 1=regression) enable quality enforcement

## Architecture

```
Source Documents
      ↓ (canonicalize, anchor)
Gold Set (stable source evidence)
      ↓ (evaluate)
Retrieval Results
      ↓ (map to source spans)
Evaluation Metrics
      ↓ (compare baseline vs candidate)
Regression Detection
      ↓ (exit code for CI)
Pass/Fail
```

## Why SPANCHOR?

### Chunk IDs are Fragile
- Change chunk size → chunk IDs change → evaluation breaks
- No continuity across retrieval pipeline modifications
- Evaluation becomes a moving target

### Source Anchors are Stable
- Character spans in canonical documents don't change when chunks do
- Evaluation remains valid across pipeline modifications
- Source evidence is the ground truth

### Per-Query Regression Detection
- Individual query regression detection prevents aggregate masking
- One query getting worse fails the gate, even if others improve
- Actionable signal for RAG engineers
```

**Why**:
- Opens with the core value: "test whether...expected source evidence"
- Explains the problem clearly (fragility of chunk IDs)
- Shows the solution visually and verbally
- Includes architecture diagram (ASCII)
- "Why" section differentiates from alternatives
- Addresses the core concern: stability

---

### 4. One-Sentence Elevator Pitch

**Recommended:**
```
SPANCHOR is a retrieval regression testing framework that anchors gold evidence
to source documents so your evaluation survives pipeline changes.
```

**Why**: 
- Identifies what it is (framework)
- Core differentiator (source anchors)
- Primary benefit (survives pipeline changes)
- One sentence, technical audience

**Alternative (simpler):**
```
Test that your RAG retriever still finds the right evidence when you change it.
```
(More casual, less technical, easier for newcomers)

---

### 5. Two-Sentence Technical Pitch

**Recommended:**
```
SPANCHOR decouples retrieval evaluation from chunking representation by anchoring
gold labels to character spans in canonical source documents. This enables stable
regression testing across retrieval pipeline modifications without rebuilding evaluation
when chunking, indexing, or retrieval algorithms change.
```

**Why**:
- First sentence explains the mechanism
- Second sentence explains the consequence
- Uses precise terminology (decoupling, canonical, regression testing)
- Addresses the core pain point: rebuilding evaluation

---

### 6. Developer-Focused Description

**Recommended:**
```markdown
## For RAG Engineers

SPANCHOR addresses a critical workflow pain: regression testing your retrieval system.

When you modify your RAG retrieval pipeline (chunking, retriever, ranker, etc.),
you need to verify that retrievals still return the expected source evidence.
Traditional approaches couple evaluation to generated chunk IDs, which break with
any retrieval representation change.

SPANCHOR solves this by:
1. Anchoring gold labels to stable source spans (not chunk IDs)
2. Mapping retrieved results back to source spans
3. Computing retrieval-agnostic metrics (Recall@K, Precision@K, Hit@K, IoU)
4. Detecting per-query regressions in a CI/CD-friendly way

**In CI**: Prevent retrieval quality degradation in your release pipeline.
**In Development**: Safely experiment with chunking, retrieval, and ranking changes.
**In Dashboards**: Track retrieval quality across configuration changes.
```

**Why**:
- Starts with the use case, not the tool
- Acknowledges the pain point directly
- Explains the limitation of existing approaches
- Lists the solution benefits clearly
- Includes concrete use cases

---

### 7. "Why SPANCHOR?" Section

**Recommended:**

```markdown
## Why SPANCHOR?

### Stability Across Changes
Traditional chunk-based evaluation breaks when you modify retrieval. SPANCHOR
evaluation is stable: source anchors are immutable, chunk representation doesn't matter.

### CI/CD Integration
Exit codes (0=pass, 1=regression) integrate naturally into release pipelines.
Prevent retrieval regressions from reaching production.

### Per-Query Visibility
See which queries regressed, by how much, and in which metrics. Actionable
insights for improving your retriever.

### No LLM Required
Retrieval evaluation shouldn't depend on LLM quality. SPANCHOR measures only
whether retrieved content covers expected evidence. Answer quality is evaluated
separately (if at all).

### Local and Deterministic
No cloud dependencies, no network calls, no telemetry. Same gold set, same
retriever, same results every time. Perfect for CI/CD, local testing, and
reproducibility.

### Minimal Dependencies
Only `typer` (CLI) and `rich` (formatting). No heavy ML frameworks.
```

**Why**:
- Differentiates from competitors
- Addresses key concerns (LLM dependency, reproducibility)
- Explains concrete benefits (CI/CD, visibility)
- No exaggerated claims
- Each section is short and actionable

---

### 8. SEO/Discoverability Keywords

**Primary keywords** (high-intent, specific):
- RAG retrieval evaluation
- Retrieval regression testing
- Source-anchored evaluation
- RAG quality testing

**Secondary keywords** (related, broader):
- RAG pipeline testing
- Retrieval quality metrics
- Retrieval comparison
- Baseline candidate evaluation
- Regression detection

**Technical keywords** (for filtering):
- Recall@K
- Precision@K
- Hit@K
- IoU metric
- Per-query evaluation

**Avoid**:
- "Production-ready" (unverified)
- "Enterprise-grade" (unverified)
- "AI platform" (misleading)
- "LLM evaluation" (incorrect scope)

---

### 9. CLI Description

**Current** (in pyproject.toml):
```
"Regression-testing for RAG retrieval pipelines using stable source-document anchors"
```

**Recommended** (same for now - it's good):
```
"Deterministic retrieval regression testing for RAG pipelines"
```

**Why**: Shorter for CLI help text, leads with core concept

---

### 10. Package Metadata Description

**For pyproject.toml:**

```toml
description = "Deterministic retrieval regression testing for RAG pipelines using source-document anchors"
```

**Why**: 
- Combines PyPI shortness with accuracy
- Shows both "what" (regression testing) and "how" (source anchors)
- Under 120 chars

---

## Differentiation Framework

### What SPANCHOR IS
- ✅ Retrieval evaluation framework
- ✅ Regression testing tool
- ✅ Source-anchor-based assessment
- ✅ Chunk-to-span mapper
- ✅ Retrieval quality metrics
- ✅ Baseline/candidate comparison
- ✅ CI/CD integration point

### What SPANCHOR IS NOT
- ❌ RAG framework (use LlamaIndex, LangChain, etc.)
- ❌ Answer quality evaluator (measure retrieval only)
- ❌ LLM evaluation tool (separate concern)
- ❌ Vector database (you provide the retriever)
- ❌ Embedding provider (use OpenAI, Cohere, etc.)
- ❌ Observability platform (no telemetry)
- ❌ Document parser (you provide documents)

**Clear messaging**: "SPANCHOR evaluates **retrieval quality**, not answer correctness."

---

## Comparison: Traditional vs. SPANCHOR

### Traditional Chunk-Based Evaluation
```
Question
   ↓
Retrieve Chunks (chunk_id_1, chunk_id_2, ...)
   ↓
Evaluate Using Chunk IDs
   ↓
❌ Problem: Chunk IDs break when retrieval changes
```

### SPANCHOR Source-Anchored Evaluation
```
Question
   ↓
Expected Source Evidence (gold anchors = stable)
   ↓
Retrieve Content (any representation)
   ↓
Map to Source Spans (chunk-independent)
   ↓
Evaluate Against Stable Evidence
   ↓
✅ Evaluation survives retrieval changes
```

**Key insight**: Decoupling source evidence from retrieval representation.

---

## Recommended Final Wordings (For Review)

### Short (PyPI - 80–120 chars)
```
Deterministic retrieval regression testing for RAG pipelines using source-document anchors.
```

### Medium (GitHub - 2 sentences)
```
Deterministic retrieval evaluation for RAG pipelines. Anchor gold evidence to source documents,
evaluate retrieved results against stable source anchors, detect retrieval regressions across
pipeline changes.
```

### Long (README)
[See Section 3 above]

### Elevator Pitch (one sentence)
```
SPANCHOR is a retrieval regression testing framework that anchors gold evidence to source
documents so your evaluation survives pipeline changes.
```

### Technical Pitch (two sentences)
```
SPANCHOR decouples retrieval evaluation from chunking representation by anchoring gold labels
to character spans in canonical source documents. This enables stable regression testing across
retrieval pipeline modifications without rebuilding evaluation when chunking, indexing, or
retrieval algorithms change.
```

---

## Why These Recommendations Are Clearer

### Current Description
```
"Regression-testing for RAG retrieval pipelines using stable source-document anchors."
```

**Issues**:
- "Stable source-document anchors" is the *how*, not immediately clear why it matters
- Doesn't explain the problem being solved
- Technical audience gets it; RAG newcomers might not
- Doesn't differentiate from "just another evaluation tool"

### Recommended Description
```
"Deterministic retrieval regression testing for RAG pipelines using source-document anchors."
```

**Improvements**:
- "Deterministic" leads with the primary benefit (stability, reproducibility)
- "Retrieval regression testing" clarifies the use case
- "Using source-document anchors" explains the mechanism
- Reads naturally: benefit first, method second
- Includes stronger SEO terms (deterministic, regression)

### Why It Works Better

1. **Benefits-first structure**: What you get (deterministic testing) before how (anchors)
2. **Clear scope**: "Retrieval" specifically (not answer evaluation)
3. **Action-oriented**: "Regression testing" is what engineers actually do
4. **Technical accuracy**: "Source-document anchors" is precise without being cryptic
5. **Differentiation**: Emphasizes stability, which existing tools don't promise
6. **Discovery**: Keywords (regression, deterministic, RAG) appear naturally

---

## Implementation Checklist

- [ ] Review recommended descriptions
- [ ] Approve or suggest modifications
- [ ] Update pyproject.toml description
- [ ] Update README.md opening section
- [ ] Update GitHub repository description
- [ ] Update CLI help text (if desired)
- [ ] Consider adding "Why SPANCHOR?" section to README
- [ ] Add differentiation table to README
- [ ] Document decision rationale (for future maintainers)

---

## Notes for Future Updates

**When to revisit descriptions**:
- After significant feature additions (v0.2.0+)
- If community feedback suggests confusion about scope
- If new use cases emerge that should be highlighted

**What NOT to change**:
- Version number
- Core package functionality
- Public API
- Existing tests
- Architecture decisions

**What CAN be refined**:
- Example code
- READMe structure
- Documentation clarity
- Description wording (ongoing)

---

## Final Recommendation

**Use the "Recommended" versions above.** They:
1. Accurately describe the product
2. Lead with the primary benefit (stability/determinism)
3. Clarify scope (retrieval evaluation, not answer quality)
4. Include differentiation (source anchors vs. chunk IDs)
5. Use precise technical terminology
6. Avoid exaggeration or unsupported claims
7. Work across PyPI, GitHub, and README contexts

**No code changes needed. Description optimization only.**

---

**Document Date**: 2026-09-30  
**Status**: Ready for review  
**Next Step**: Approval before applying to production descriptions
