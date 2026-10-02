# SPANCHOR Frontend Website — Comprehensive Product, Design & Engineering Specification

**Document Version:** 1.0.0  
**Target Audience:** Frontend Engineers, UI/UX Designers, Product Managers, Technical Reviewers  
**Theme Policy:** Light Theme Only  
**Backend Policy:** Zero Backend / 100% Deterministic Local Frontend Engine  

---

## 1. PRODUCT DESIGN DIRECTION

### Design Philosophy
SPANCHOR is a developer tool for source-anchored regression testing in RAG (Retrieval-Augmented Generation) pipelines. Its visual and interaction design must reflect the rigor, clarity, and precision of developer infrastructure tools.

The interface must convey:
- **Technical & Developer-Focused:** Clean typography, code-first representations, raw data visibility, clear diagnostic signals.
- **Professional & Precise:** Grid-aligned layouts, strict typography hierarchy, high contrast data tables, mathematical accuracy in metrics.
- **Minimal & Trustworthy:** No unnecessary visual noise, no generic AI SaaS fluff (floating spheres, cosmic gradients, glow effects), clear separation of content and control.
- **Documentation-First & Production-Quality:** Structured reading flows, dense information architecture, copyable code, accessible UI components.

### Visual Influences
Drawing inspiration from modern developer platforms without copying branding or layouts:
- **GitHub:** Dense data tables, status badges, diff visualizations, neutral monochromatic gray scales with crisp borders.
- **Vercel:** Sharp layout grids, refined typography spacing, responsive navigation drawers, clean micro-interactions.
- **Stripe Documentation:** Multi-column layouts, clear code blocks with copy controls, sticky table-of-contents, structured callouts.
- **Modern Developer Tools (e.g., Turborepo, Supabase, Tailwind UI):** Clean badge styling, monospaced data alignment, intuitive filter controls.

### Antipatterns & Design Exclusions
- **No Dark Mode:** Light theme only (`#FFFFFF` background, `#0F172A` text, `#F8FAFC` muted panels).
- **No Cyberpunk / Neon Aesthetics:** No glowing neon outlines, radial glows, or dark cosmic gradients.
- **No Excessive Glassmorphism:** Standard opaque containers with clean 1px borders (`border-slate-200`).
- **No Giant Decorative Graphics:** Avoid 3D floating rendered shapes, stock imagery, or generic AI robot illustrations.
- **No Generic AI SaaS Layouts:** Avoid giant centered hero text with floating blur spheres and feature cards with 24px border radii.
- **No Unnecessary Animations:** Motion is reserved exclusively for state execution, simulation progress, and modal transitions.
- **No Fluff Marketing Copy:** Avoid claims such as "world's best", "revolutionary", "guaranteed 100% accurate".

### Design Tokens & Token Architecture

#### Visual Hierarchy
- **Primary Focus:** Interactive Simulation & Code Editor (`CODE → RUN → VISUALIZATION`).
- **Secondary Focus:** Interactive Metric & Regression Comparison Panels.
- **Tertiary Focus:** Documentation & Architectural Deep Dives.

#### Spacing Philosophy
Built on an **8px base grid** with a 4px micro-grid:
- `space-1` (4px): Micro gaps (badge icons, button inline spacing).
- `space-2` (8px): Tight component padding (compact inputs, table cell vertical padding).
- `space-3` (12px): Standard component internal padding (buttons, input fields).
- `space-4` (16px): Card padding, container gaps.
- `space-6` (24px): Section gaps within cards, toolbar spacing.
- `space-8` (32px): Sub-section margins.
- `space-12` (48px): Major component gaps.
- `space-16` (64px): Hero & section vertical padding.

#### Typography System
- **Primary Body Font:** `Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`, `sans-serif`.
- **Code & Monospace Font:** `JetBrains Mono`, `Fira Code`, `ui-monospace`, `SFMono-Regular`, `Menlo`, `Monaco`, `Consolas`, monospace.

| Scale Class | Font Size | Line Height | Weight | Usage |
|---|---|---|---|---|
| `text-xs` | 12px | 16px | 400 / 500 | Metadata, table headers, inline tags, badge text |
| `text-sm` | 14px | 20px | 400 / 500 / 600 | Body default, button labels, sidebar nav, code comments |
| `text-base` | 16px | 24px | 400 / 500 | Lead paragraphs, card titles, form inputs |
| `text-lg` | 18px | 28px | 600 | Sub-section headings (H4), metric summary headers |
| `text-xl` | 20px | 28px | 600 | Section titles (H3), modal headers |
| `text-2xl` | 24px | 32px | 600 / 700 | Major section titles (H2), doc page titles |
| `text-4xl` | 36px | 44px | 700 | Page titles (H1), hero subhead emphasis |
| `text-5xl` | 48px | 56px | 800 | Landing Page Hero Headline |

#### Color System (Light Theme Only)
- **Background Main:** `#FFFFFF` (`bg-white`)
- **Background Subtly Muted:** `#F8FAFC` (`bg-slate-50`)
- **Background Card / Panel:** `#FFFFFF` (`bg-white`) with `#F1F5F9` (`bg-slate-100`) headers
- **Border Default:** `#E2E8F0` (`border-slate-200`)
- **Border Strong:** `#CBD5E1` (`border-slate-300`)
- **Border Dark (Terminal):** `#334155` (`border-slate-700`)
- **Text Main:** `#0F172A` (`text-slate-900`)
- **Text Muted:** `#475569` (`text-slate-600`)
- **Text Subtle:** `#64748B` (`text-slate-500`)
- **Text Disabled:** `#94A3B8` (`text-slate-400`)

##### Semantic Accent Palette
- **Primary Brand Accent (Sky/Teal):** `#0284C7` (`sky-600`), hover `#0369A1` (`sky-700`), light bg `#F0F9FF` (`sky-50`)
- **Success / Improved State:** `#166534` text (`emerald-800`), `#DCFCE7` bg (`emerald-100`), `#16A34A` icon (`emerald-600`)
- **Warning / Regressed State:** `#991B1B` text (`red-800`), `#FEE2E2` bg (`red-100`), `#DC2626` icon (`red-600`)
- **Neutral / Unchanged State:** `#334155` text (`slate-700`), `#F1F5F9` bg (`slate-100`), `#64748B` icon (`slate-500`)
- **Anchor Highlight (Span):** `#FEF08A` bg (`yellow-200`), `#854D0E` text (`yellow-800`), border `#FDE047` (`yellow-300`)

#### Borders, Shadows & Radius
- **Border Width:** 1px standard (`border`), 2px focused (`border-2`).
- **Corner Radius:**
  - Badges / Inline Code: `rounded` (4px)
  - Buttons / Inputs / Cards / Panels: `rounded-md` (6px)
  - Hero Containers / Modals: `rounded-lg` (8px)
  - Pills / Status Indicator Dots: `rounded-full` (9999px)
- **Shadows:** Minimal, non-blurry shadows.
  - Default Cards: `shadow-sm` (`0 1px 2px 0 rgb(0 0 0 / 0.05)`)
  - Dropdowns / Popovers: `shadow-md` (`0 4px 6px -1px rgb(0 0 0 / 0.1)`)
  - Floating Panels: `shadow-lg` (`0 10px 15px -3px rgb(0 0 0 / 0.1)`)

#### Iconography
- **Library:** `Lucide React`
- **Style:** 1.5px or 2px stroke width, matching adjacent font color and size.
- **Key Icons:** `Play`, `RotateCcw`, `Check`, `AlertTriangle`, `ArrowRight`, `ChevronRight`, `Copy`, `FileText`, `Search`, `ExternalLink`, `GitBranch`, `Terminal`, `Sliders`, `ShieldCheck`.

#### Interaction States
- **Default:** Crisp border, neutral background.
- **Hover:** Darker text/border, subtle background shift (`bg-slate-50` or `bg-sky-50`).
- **Focus:** Clear 2px ring with 2px offset (`focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-600 focus-visible:ring-offset-2`).
- **Active:** Scaled down slightly (`active:scale-[0.98]`), dark accent background (`bg-sky-700`).
- **Disabled:** `opacity-50 cursor-not-allowed pointer-events-none`.

---

## 2. BRAND SYSTEM

### Brand Identity & Positioning
- **Brand Name:** SPANCHOR
- **Tagline / Core Positioning Statement:**  
  *"Source-anchored regression testing for RAG retrieval pipelines."*
- **Value Proposition:** Traditional RAG evaluations rely on fragile chunk IDs or fuzzy semantic scores that break whenever chunk size, overlap, or embedding models change. SPANCHOR anchors ground-truth evidence directly to original source text spans, enabling exact, deterministic regression testing across pipeline iterations.

### Visual Brand Elements
- **Logo Treatment:** Monospaced text bracket symbol paired with bold uppercase wordmark:  
  `[anchor]` `SPANCHOR`
  - Symbol: `[#]` or `[⚓]` enclosed in slate-800 brackets.
  - Primary Logo Layout: Inline `flex items-center gap-2 font-mono font-bold tracking-tight text-slate-900`.
- **Wordmark Styling:** Inter font, Weight 800 (ExtraBold), uppercase, tracking-tight (`-0.025em`).
- **Favicon Concept:** A dark slate-900 square with rounded corners (4px) containing a cyan `#0284C7` source span symbol `[⎺]` in vector SVG format.

### Typography Rules
- **Brand Headings:** Inter ExtraBold (H1), Bold (H2, H3).
- **Code & API Names:** JetBrains Mono Medium (`font-mono font-medium text-slate-800`).
- **Badges & Tags:** JetBrains Mono SemiBold, 11px uppercase (`tracking-wider text-[11px]`).

```
[ SPANCHOR ] v0.1.0  |  Source-Anchored RAG Evaluation
```

---

## 3. INFORMATION ARCHITECTURE

### Complete Route Map & Sitemap

```
/ (Landing Page)
├── /docs (Docs Overview / Introduction)
│   ├── /docs/installation
│   ├── /docs/quickstart
│   ├── /docs/concepts
│   ├── /docs/anchors
│   ├── /docs/gold-sets
│   ├── /docs/metrics
│   ├── /docs/comparison
│   ├── /docs/adapters
│   ├── /docs/cli
│   ├── /docs/testing
│   └── /docs/limitations
├── /playground (Interactive Simulation IDE)
├── /examples (Code Examples & Workflows)
├── /api (API Reference Specification)
└── /architecture (Pipeline Architecture Visualizer)
```

### Route Descriptions & Purpose

| Route | Purpose | Key Content & Interactive Components |
|---|---|---|
| `/` | Landing & Conversion | Hero, Pipeline Diagram, Interactive Demo, Source Anchor Explainer, Baseline vs Candidate, Metrics Grid, "What SPANCHOR is Not", CTAs |
| `/docs` | Documentation Hub | Introduction to SPANCHOR, core principles, link cards to all sub-topics |
| `/docs/installation` | Setup Guide | Pip install commands, Python requirements, virtual environment setup |
| `/docs/quickstart` | 5-Minute Tutorial | Step-by-step minimal evaluation example with copyable code |
| `/docs/concepts` | Core Concepts | Explanation of Source Anchors vs Chunk IDs, RAG Regressions |
| `/docs/anchors` | Anchor Specification | How text spans, SHA-256 hashes, and offsets are computed and matched |
| `/docs/gold-sets` | Dataset Format | JSON schema for queries, source document references, and gold spans |
| `/docs/metrics` | Metric Catalog | Hit@K, Recall@K, Precision@K, IoU, Full Evidence@K formulas & definitions |
| `/docs/comparison` | Evaluation & Delta | How baseline vs candidate comparisons work objectively |
| `/docs/adapters` | Framework Integration | LangChain, LlamaIndex, and custom retriever adapter specifications |
| `/docs/cli` | Command Line Tool | `spanchor evaluate`, `spanchor compare` flags and CI integration |
| `/docs/testing` | Pytest & CI/CD | Running SPANCHOR in GitHub Actions and regression test suites |
| `/docs/limitations` | Scope Boundaries | Out-of-scope capabilities (e.g. LLM judge generation, vector database) |
| `/playground` | Full Simulation Workspace | Code Editor, Interactive Execution State Machine, Document Span Viewer, Metric Cards, Filterable Regression Table |
| `/examples` | Workflow Library | 6 runnable code examples with side-by-side expected outputs |
| `/api` | API Reference | Formal specification of Python classes (`Document`, `Anchor`, `Span`, `evaluate()`) |
| `/architecture` | Pipeline Visualizer | Interactive 8-step RAG evaluation pipeline with node inspection cards |

### Navigation Architecture
- **Global Header Navbar:**
  - Left: Brand Logo (`[anchor] SPANCHOR`) with version badge (`v0.1.0`).
  - Center: Nav links (`Docs`, `Playground`, `Examples`, `API`, `Architecture`).
  - Right: GitHub Link (Star counter badge), PyPI Package Link (`pip install spanchor`), Quick Search trigger (`Ctrl+K` visual key pill).
- **Global Footer Navigation:**
  - Column 1: Brand & Tagline + License (MIT).
  - Column 2: Product (`Playground`, `Examples`, `Architecture`, `API`).
  - Column 3: Documentation (`Quickstart`, `Concepts`, `Source Anchors`, `Metrics`, `CLI`).
  - Column 4: Community & Links (`GitHub Repository`, `PyPI Release`, `Issue Tracker`).
- **Documentation Navigation (Left Sidebar):**
  - Sticky vertical menu categorized into sections: *Getting Started*, *Core Concepts*, *Evaluation*, *Integrations*, *Reference*.
- **Documentation On-Page Navigation (Right Table of Contents):**
  - Sticky auto-highlighting headings tracker (H2, H3).
- **Mobile Navigation:**
  - Header hamburger button triggering a full-height clean drawer with navigation links and search trigger.

---

## 4. USER EXPERIENCE & USER JOURNEYS

### Journey 1: First-Time Visitor (Discovery to Installation)
1. **Landing Page (`/`):** Reads Hero headline *"Regression testing for RAG retrieval"*.
2. **Interactive Demo:** Clicks *"Try Interactive Demo"* or scrolls to the inline simulation.
3. **Execution:** Clicks **Run Simulation**, watches state progression, terminal output, and metric card updates.
4. **Anchor Understanding:** Scrolls to Source Anchor visualizer; clicks on evidence span to see hash matching.
5. **Docs & Install:** Clicks *"Read Documentation"* or copies `pip install spanchor` from header CTA.

### Journey 2: Developer (Hands-on Exploration)
1. **Direct Navigation:** Navigates directly to `/playground`.
2. **Preset Selection:** Switches between `CloudSync Demo` and custom query examples.
3. **Simulation Execution:** Edits python parameters visually, hits **Run**, inspects regression output table.
4. **Table Filter:** Filters regression table by `STATUS: REGRESSED` to find failing query anchors.
5. **Quickstart:** Clicks *"View Quickstart"* to implement in their own project via PyPI.

### Journey 3: Technical Evaluator / Architect (Rigor & Metrics Inspection)
1. **Landing to Architecture:** Navigates to `/architecture` to review canonical pipeline integration.
2. **Metrics Inspection:** Navigates to `/docs/metrics` to verify exact formulas for Hit@K, Recall@K, and IoU.
3. **Comparison Validation:** Checks baseline vs candidate delta calculations on `/playground` or `/docs/comparison`.
4. **API Verification:** Inspects Python type signatures on `/api`.
5. **GitHub Link Out:** Navigates to external GitHub repository for source code inspection.

### Journey 4: Existing SPANCHOR User (Reference & Integration)
1. **Docs Lookup:** Navigates to `/docs/cli` or `/docs/adapters`.
2. **Code Copying:** Uses one-click copy on LangChain/LlamaIndex code snippets.
3. **Pytest Integration:** Copies GitHub Actions workflow snippet from `/docs/testing`.

---

## 5. LANDING PAGE DESIGN & COMPOSITION

### Section Order & Layout Breakdown

```
┌─────────────────────────────────────────────────────────┐
│ 1. Global Navbar                                        │
├─────────────────────────────────────────────────────────┤
│ 2. Hero Section (Headline, Subhead, CTAs, Pipeline Diagram)│
├─────────────────────────────────────────────────────────┤
│ 3. Interactive Code -> Run -> Execution -> Metrics Demo │
├─────────────────────────────────────────────────────────┤
│ 4. Source Anchor Visualizer (Document Span vs Chunk Hash)│
├─────────────────────────────────────────────────────────┤
│ 5. Baseline vs Candidate Regression Comparison Panel   │
├─────────────────────────────────────────────────────────┤
│ 6. Metrics Breakdown Grid (Hit@K, Recall@K, IoU)        │
├─────────────────────────────────────────────────────────┤
│ 7. How SPANCHOR Works (4-Step Canonical Architecture)   │
├─────────────────────────────────────────────────────────┤
│ 8. "What SPANCHOR Is Not" (Scope Boundary Matrix)       │
├─────────────────────────────────────────────────────────┤
│ 9. Quickstart & Installation CTA                        │
├─────────────────────────────────────────────────────────┤
│ 10. External Links CTA (GitHub & PyPI Badges)           │
├─────────────────────────────────────────────────────────┤
│ 11. Global Footer                                       │
└─────────────────────────────────────────────────────────┘
```

### Section-by-Section Specifications

#### Section 1: Global Navbar
- **Content:** Logo `[anchor] SPANCHOR`, version `v0.1.0`, main nav items, GitHub stars badge, PyPI package button.
- **Layout:** Sticky top, `h-16`, flex row, container `max-w-7xl`, backdrop border `border-b border-slate-200 bg-white/95 backdrop-blur-sm z-50`.
- **Responsive:** Nav items hide on `< 768px`; mobile hamburger icon displays.

#### Section 2: Hero Section
- **Content:** Title H1, Subtitle paragraph, CTA button cluster, Pipeline flow visualizer.
- **Layout:** Centered content header (`max-w-4xl mx-auto text-center py-16`), followed by full-width interactive diagram panel (`max-w-6xl mx-auto`).

#### Section 3: Interactive Demo (Code → Run → Terminal → Metrics)
- **Objective:** Give instant hands-on visual proof of evaluation execution.
- **Layout:** Two-column desktop grid (`lg:grid-cols-12 gap-6`). Left column (5 cols): Code Editor & Run Controls. Right column (7 cols): Terminal Stream + Live Metric Output. Below: Regression Summary Table.

#### Section 4: Source Anchor Explanation
- **Objective:** Demystify how SPANCHOR anchors text spans instead of chunk IDs.
- **Layout:** Split layout (`lg:grid-cols-2 gap-8`). Left: Explanation copy with bulleted technical benefits. Right: Interactive Document Span Inspector.

#### Section 5: Baseline vs Candidate Comparison
- **Objective:** Demonstrate regression analysis between two retriever versions.
- **Layout:** Dual metric column card comparison with delta pills (`-0.156`, `-0.003`) and query status counts (`6 Improved`, `75 Unchanged`, `19 Regressed`).

#### Section 6: Metrics Grid
- **Objective:** Catalog the evaluation metrics calculated by SPANCHOR.
- **Layout:** 3-column grid of metric cards (Hit@K, Recall@K, Precision@K, IoU, Full Evidence@K, Character Coverage).

#### Section 7: How SPANCHOR Works
- **Objective:** Explain the 4-step canonical workflow (Canonicalize → Anchor → Match → Metric).
- **Layout:** 4-step horizontal process cards with connecting arrow indicators.

#### Section 8: What SPANCHOR Is Not
- **Objective:** Prevent misunderstanding of scope boundaries.
- **Layout:** 2-column checklist matrix (Green "What SPANCHOR Is" vs Gray "What SPANCHOR Is Not").

#### Section 9 & 10: CTAs & Installation
- **Objective:** Convert visitor to install or star repository.
- **Layout:** Light slate card (`bg-slate-900 text-white rounded-xl p-10`) with `pip install spanchor` copy block and GitHub primary button.

#### Section 11: Global Footer
- **Layout:** 4-column structured navigation footer with copyright and license terms.

---

## 6. HERO DESIGN

### Copy Specification
- **Headline (H1):** `"Regression testing for RAG retrieval."`
- **Subheadline:** `"Validate whether your retrieval pipeline still finds the evidence it needs — using stable source anchors instead of fragile chunk IDs."`
- **Primary CTA Button:** `"Try Interactive Demo"` (Scrolls down smoothly to Section 3 / Navigates to `/playground`).
- **Secondary CTA Button:** `"Read Documentation"` (Navigates to `/docs`).
- **Pill Badge Above Title:** `[SPANCHOR v0.1.0] Source-Anchored Retrieval Evaluation`

### Interactive Hero Visual Diagram
An animated horizontal node pipeline representing RAG evaluation flow:

```
[ Question ] ──► [ Retriever ] ──► [ Retrieved Evidence ] ──► [ SPANCHOR ] ──► [ Evaluation ] ──► [ Regression Result ]
```

#### Animation & Behavior
- **Node Highlighting:** A subtle cyan focus glow cycles sequentially through nodes every 1.5 seconds when idle.
- **Hover Interaction:** Hovering any node pauses cycling and highlights the node's payload preview box below:
  - *Question Node:* Displays `Query 001: "CloudSync SSL port config"`
  - *Retriever Node:* Displays `BM25 + Vector Hybrid (Top-K=5)`
  - *Retrieved Evidence Node:* Displays `Doc ID: cs-deploy-guide.md (Span: 142-288)`
  - *SPANCHOR Node:* Displays `Matching SHA-256 Text Span Hash...`
  - *Evaluation Node:* Displays `Recall@5: 0.405 | IoU: 0.78`
  - *Regression Result Node:* Displays `Status: 19 Regressions Detected (⚠)`

---

## 7. SIGNATURE EXPERIENCE: FRONTEND EXECUTION SIMULATION

### Concept & Guiding Principles
The core visual experience of SPANCHOR is the simulation of a Python evaluation run:

```
CODE ──► RUN ──► EXECUTION ──► RETRIEVAL ──► ANCHORS ──► METRICS ──► REGRESSION
```

### Deterministic Rule & Safety Constraints
- **Zero Backend / Zero Pyodide:** No actual Python code execution, no WebAssembly Python runtimes, no `eval()`.
- **Pure Local State Simulation:** The simulation is powered by a deterministic TypeScript state machine using hardcoded demo dataset fixtures (`CloudSync Demo`).
- **100% Determinism:** Running the simulation N times with identical parameters produces 100% identical terminal logs, metrics, and regression tables.

---

## 8. CODE EDITOR DESIGN

### UI Component Specification
- **Header Toolbar:**
  - Left: File label `eval_pipeline.py` with Python language icon.
  - Center: Preset Selector Dropdown (`CloudSync Demo`, `Support Bot RAG`, `Medical Docs RAG`).
  - Right: `Copy Code` button, `Reset` button.
- **Code Container:**
  - Dark terminal/editor theme frame (`bg-slate-900 text-slate-100 rounded-md border border-slate-800`).
  - Line numbers in left gutter (`text-slate-600 select-none pr-4 font-mono text-xs`).
  - Syntax highlighted code block (keywords `#0284C7`, strings `#10B981`, comments `#64748B`, functions `#F59E0B`).
- **Bottom Toolbar:**
  - Run Simulation Button: Primary action (`bg-sky-600 hover:bg-sky-700 text-white font-medium px-4 py-2 rounded-md flex items-center gap-2`).
  - Keyboard Shortcut Hint: `Ctrl + Enter` / `⌘ + Enter`.

### Displayed Code Snippet Example
```python
from spanchor import evaluate, GoldSet, RetrievalResult

# 1. Load ground truth source anchors
gold_set = GoldSet.from_json("cloudsync_gold_set.json")

# 2. Evaluate candidate retrieval output
results = evaluate(
    gold_set=gold_set,
    retrieved_results="candidate_retrieval.json",
    top_k=[1, 3, 5],
    metric_threshold=0.5
)

# 3. Print regression summary
results.print_summary()
```

---

## 9. EXECUTION SIMULATION STATE MACHINE

### State Machine Diagram

```
[ IDLE ] ──(Click RUN)──► [ LOADING_DATA ] ──► [ LOADING_GOLD_SET ] ──► [ EVALUATING ]
                                                                             │
[ COMPLETE ] ◄── [ COMPARING ] ◄── [ CALCULATING_METRICS ] ◄── [ MATCHING_ANCHORS ]
```

### Complete State Transition Table

| State Name | Duration | Progress % | Terminal Output Line Emitted | UI Visual State |
|---|---|---|---|---|
| `IDLE` | Static | 0% | `$ spanchor evaluate --gold-set cloudsync.json` | Run button active, terminal ready |
| `LOADING_DATA` | 300ms | 15% | `[1/6] Loading retrieved candidate results... (100 queries)` | Progress bar begins |
| `LOADING_GOLD_SET` | 400ms | 30% | `[2/6] Loading source anchor gold set... (100 ground truth spans)` | Loading spinner on step 2 |
| `EVALUATING` | 500ms | 50% | `[3/6] Evaluating query evidence spans against retrieved chunks...` | Query counter ticks 1..100 |
| `MATCHING_ANCHORS` | 600ms | 70% | `[4/6] Matching SHA-256 text span hashes... (Exact matches: 81)` | Anchor badge pulse animation |
| `CALCULATING_METRICS` | 400ms | 85% | `[5/6] Calculating Recall@5, Precision@5, Hit@5, IoU...` | Metric cards show skeletons |
| `COMPARING` | 300ms | 95% | `[6/6] Computing baseline vs candidate regression deltas...` | Regression table skeleton |
| `COMPLETE` | Static | 100% | `✓ Evaluation complete. 19 regressions detected.` | Metric values lock, table populates |

---

## 10. TERMINAL DESIGN

### Terminal Visual & Styling
- **Background:** `#0F172A` (`bg-slate-900`)
- **Border:** `#334155` (`border-slate-700`)
- **Header Bar:** Mac/Linux style window controls (3 small dots: `#EF4444`, `#F59E0B`, `#10B981`) + Title `bash — spanchor CLI`.
- **Font:** `JetBrains Mono`, 13px, line-height 1.6.
- **Scroll Behavior:** Auto-scrolls to bottom as terminal lines append during simulation. Re-enable user scroll on hover.

### Terminal Output Stream Format Example
```bash
$ spanchor evaluate --baseline v1_bm25.json --candidate v2_hybrid.json

Loading dataset: CloudSync Deployment Docs (100 Queries)
Reading baseline metrics...  Recall@5: 0.405 | Hit@5: 0.410
Reading candidate results...

Evaluating queries:
Query 001 [CS-Q-101] ............................... ✓ MATCHED (IoU: 1.00)
Query 002 [CS-Q-102] ............................... ✓ MATCHED (IoU: 0.85)
Query 003 [CS-Q-103] ............................... ⚠ REGRESSED (Anchor Miss)
... [97 additional queries processed] ...

Computing final evaluation metrics:
--------------------------------------------------
Metric         Baseline    Candidate   Delta      Status
--------------------------------------------------
Recall@5       0.405       0.249       -0.156     ⚠ REGRESSED
Precision@5    0.020       0.017       -0.003     ⚠ REGRESSED
Hit@5          0.410       0.260       -0.150     ⚠ REGRESSED
IoU            0.782       0.512       -0.270     ⚠ REGRESSED
--------------------------------------------------

Summary:
- Total Queries Evaluated: 100
- Improved Queries:      6  (  6.0% )
- Unchanged Queries:     75 ( 75.0% )
- Regressed Queries:     19 ( 19.0% )

Execution finished in 1.42s.
$ _
```

---

## 11. SOURCE ANCHOR VISUALIZATION

### Concept: Source Anchors vs Fragile Chunk IDs
Chunk IDs change whenever chunking strategy, chunk size, overlap, or embedding models change. SPANCHOR anchors ground-truth evidence directly to source text spans identified by document ID, character offset ranges, and SHA-256 hashes of canonicalized text.

### Interactive Document Viewer Component
Displays an interactive document excerpt (`CloudSync deployment documentation`) with highlighted evidence text spans:

```
┌────────────────────────────────────────────────────────────────────────┐
│ Document: docs/cloudsync/deployment.md  [Hash: a7f8c92e...]          │
├────────────────────────────────────────────────────────────────────────┤
│ ... To configure the production deployment, ensure that SSL port 8443  │
│ is open in your firewall settings.                                     │
│                                                                        │
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │ [SOURCE ANCHOR #001]                                               │ │
│ │ "Database connection strings must use the sslmode=verify-full     │ │
│ │ parameter when connecting to PostgreSQL cluster instances."        │ │
│ └────────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│ The default timeout for connection pooling is set to 30 seconds ...    │
└────────────────────────────────────────────────────────────────────────┘
```

### Anchor Metadata Inspection Card
Clicking or hovering over the highlighted yellow span displays an inspector card:

| Field | Value |
|---|---|
| **Document Path** | `docs/cloudsync/deployment.md` |
| **Start Offset** | `142` |
| **End Offset** | `288` |
| **Span Length** | `146 characters` |
| **Canonical SHA-256** | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| **Match Status** | `✓ SPAN_MATCHED` (Overlap IoU = 0.94) |

---

## 12. BASELINE / CANDIDATE EXPERIENCE

### Comparison Panel Layout
A side-by-side comparison interface showing metric differences between a **Baseline** retriever (e.g., BM25) and a **Candidate** retriever (e.g., Hybrid Vector Search).

```
┌──────────────────────────────┬──────────────────────────────┐
│ BASELINE RETRIEVER (v1)      │ CANDIDATE RETRIEVER (v2)     │
├──────────────────────────────┼──────────────────────────────┤
│ Recall@5:      0.405         │ Recall@5:      0.249 (-0.156)│
│ Precision@5:   0.020         │ Precision@5:   0.017 (-0.003)│
│ Hit@5:         0.410         │ Hit@5:         0.260 (-0.150)│
└──────────────────────────────┴──────────────────────────────┘
```

### Objective Descriptive Phrasing Rule
- **Allowed Terms:** `Improved (+0.12)`, `Unchanged (0.00)`, `Regressed (-0.15)`, `Delta`, `Baseline Metric`, `Candidate Metric`.
- **Forbidden Terms:** "Winner", "Loser", "Better", "Worse", "Superior", "Defeated". All descriptions must remain strictly factual and numerical.

---

## 13. REGRESSION VISUALIZATION

### Visual Elements & Cards
- **Metric Change Cards:** Displays baseline value, candidate value, numerical delta, and status tag.
- **Query Outcome Summary Pills:**
  - `IMPROVED`: `#DCFCE7` background, `#166534` text, Icon `ArrowUpRight`
  - `UNCHANGED`: `#F1F5F9` background, `#334155` text, Icon `Minus`
  - `REGRESSED`: `#FEE2E2` background, `#991B1B` text, Icon `AlertTriangle`

### Accessible Color-Independent Indicators
Every status tag MUST combine 3 distinct visual cues to comply with accessibility rules:
1. **Text Label:** Full uppercase word (`REGRESSED`, `IMPROVED`, `UNCHANGED`).
2. **Icon Symbol:** Distinct Lucide icon (`AlertTriangle` for regressed, `TrendingUp` for improved, `Minus` for unchanged).
3. **Shape Indicator:** Square pill for Regressed, Rounded Pill for Improved, Rectangle for Unchanged.

---

## 14. REGRESSION TABLE UX

### Table Columns & Data Definition
1. **Query ID:** Monospace ID (e.g., `CS-Q-101`).
2. **Query Text:** Full query text string with inline highlight.
3. **Baseline Metric:** Numerical score (e.g., `0.405`).
4. **Candidate Metric:** Numerical score (e.g., `0.249`).
5. **Delta:** Signed numerical difference (e.g., `-0.156`).
6. **Status Badge:** Accessible status indicator.

### Interactive Controls
- **Search Bar:** Real-time client-side text filtering against Query ID and Query Text.
- **Status Filter Tabs:** `All (100)`, `Regressed (19)`, `Improved (6)`, `Unchanged (75)`.
- **Sortable Headers:** Click to sort by Query ID, Baseline Score, Candidate Score, or Delta magnitude.
- **Pagination / Rows per page:** 10, 25, 50, 100 rows.

### Table States
- **Loading State:** Skeleton table rows (`animate-pulse h-10 bg-slate-100 rounded`).
- **Empty Filter State:** `"No queries match your current filter settings."` + `Reset Filters` button.
- **Mobile Responsive State:** Converts standard table rows into individual structured stacked query cards on screen widths `< 640px`.

---

## 15. METRICS SPECIFICATION & FORMULAS

### Metric Catalog

#### 1. Hit@K
- **Definition:** Indicates whether at least one ground-truth source anchor span is retrieved within the top K results.
- **Formula:**
  $$\text{Hit}@K = \begin{cases} 1 & \text{if } \sum_{i=1}^{K} \text{Match}(\text{retrieved}_i, \text{gold}) > 0 \\ 0 & \text{otherwise} \end{cases}$$
- **Interpretation:** Binary success check for retrieval presence.

#### 2. Recall@K
- **Definition:** Fraction of total ground-truth evidence character spans retrieved in the top K results.
- **Formula:**
  $$\text{Recall}@K = \frac{|\text{Retrieved Spans in Top K} \cap \text{Gold Spans}|}{|\text{Gold Spans}|}$$
- **Interpretation:** Measures completeness of retrieved evidence.

#### 3. Precision@K
- **Definition:** Proportion of retrieved character length in top K results that overlaps with ground-truth source anchors.
- **Formula:**
  $$\text{Precision}@K = \frac{|\text{Retrieved Spans in Top K} \cap \text{Gold Spans}|}{\sum_{i=1}^{K} \text{Length}(\text{retrieved}_i)}$$
- **Interpretation:** Measures signal-to-noise ratio in retrieved text.

#### 4. IoU (Intersection over Union)
- **Definition:** The ratio of character overlap area to total combined character span area between retrieved chunk and gold anchor.
- **Formula:**
  $$\text{IoU} = \frac{\text{Length}(\text{Retrieved Span} \cap \text{Gold Span})}{\text{Length}(\text{Retrieved Span} \cup \text{Gold Span})}$$
- **Interpretation:** Evaluates exact span boundary accuracy.

#### 5. Full Evidence@K
- **Definition:** Binary indicator (1 or 0) whether ALL required source anchor spans for a multi-span query are present in top K.
- **Formula:**
  $$\text{Full Evidence}@K = \prod_{s \in \text{Gold Spans}} \mathbb{I}(\text{Retrieved in Top K}(s))$$

#### 6. Retrieved Characters
- **Definition:** Total raw character count returned to the downstream LLM context.
- **Interpretation:** Measures context window load and token efficiency.

---

## 16. PLAYGROUND DESIGN (`/playground`)

### Layout Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│ Playground Header (Preset: CloudSync Demo | Controls: Run, Reset, Replay)│
├───────────────────────────────────┬────────────────────────────────────┤
│ Left Pane (50%): Code Editor      │ Right Pane (50%): Simulation View  │
│ - Python setup snippet            │ - Terminal Execution Log           │
│ - Parameters config               │ - Live Metric Delta Cards          │
├───────────────────────────────────┴────────────────────────────────────┤
│ Bottom Section: Full Width Interactive Regression Table               │
│ - Search, Status Filters, Column Sorting, Query Detail Inspector      │
└────────────────────────────────────────────────────────────────────────┘
```

### Controls & Actions
- **Run Button:** Triggers the deterministic simulation state machine from `IDLE` to `COMPLETE`.
- **Reset Button:** Restores playground state to `IDLE` and clears execution logs.
- **Replay Button:** Re-runs the terminal animation without resetting metric parameters.

---

## 17. DOCUMENTATION DESIGN (`/docs`)

### Documentation Layout System
- **Left Sidebar (Fixed/Sticky 260px):** Categorized tree navigation with active route highlighting (`bg-sky-50 text-sky-700 font-semibold border-r-2 border-sky-600`).
- **Main Content Column (Max-W 768px):** Clean reading column with H1, breadcrumbs, content sections, code blocks, callouts, and Prev/Next links.
- **Right Sidebar (Fixed/Sticky 220px):** "On this page" auto-scrolling header index (H2/H3 tags).

### Reusable Documentation Components

#### 1. CodeBlock
- Includes language badge (`python`, `json`, `bash`), line numbers, copy button with checkmark feedback timer (2 seconds).

#### 2. InlineCode
- Styled with `bg-slate-100 text-slate-800 font-mono text-xs px-1.5 py-0.5 rounded border border-slate-200`.

#### 3. Callout Boxes
- **Note:** Slate border & icon (`bg-slate-50 border-slate-300 text-slate-800`).
- **Tip:** Emerald border & icon (`bg-emerald-50 border-emerald-300 text-emerald-900`).
- **Warning:** Amber border & icon (`bg-amber-50 border-amber-300 text-amber-900`).
- **Important:** Sky border & icon (`bg-sky-50 border-sky-300 text-sky-900`).

#### 4. Navigation Controls
- **Breadcrumbs:** `Docs > Concepts > Source Anchors`
- **Pagination Footer:** `← Previous: Quickstart` | `Next: Gold Sets →`

---

## 18. EXAMPLES DESIGN (`/examples`)

### Example Collection Specs
The `/examples` page hosts 6 runnable, copyable reference workflows:

1. **Basic Evaluation (`basic_eval.py`):** Minimal setup evaluating a single retriever against a gold set.
2. **Baseline vs Candidate Comparison (`compare_retrievers.py`):** Running delta analysis between BM25 and Hybrid search.
3. **Custom Source Anchors (`custom_anchors.py`):** Programmatically creating ground-truth spans with character offsets.
4. **LangChain Adapter (`langchain_integration.py`):** Wrapping a LangChain `VectorStoreRetriever` for evaluation.
5. **LlamaIndex Adapter (`llamaindex_integration.py`):** Evaluating a LlamaIndex `VectorIndexRetriever`.
6. **Gold Set Import/Export (`goldset_io.py`):** Loading and validating JSON gold set schemas.

---

## 19. API DESIGN (`/api`)

### Python API Reference Specification
All documented API classes and methods on `/api` represent verified core concepts:

```python
class Document(BaseModel):
    doc_id: str
    content: str
    metadata: Dict[str, Any] = {}

class Span(BaseModel):
    doc_id: str
    start_offset: int
    end_offset: int
    text_hash: str

class Anchor(BaseModel):
    anchor_id: str
    spans: List[Span]
    canonical_text: str

class EvaluationResult(BaseModel):
    metrics: Dict[str, float]
    regressions: List[QueryRegression]
    query_count: int

def evaluate(
    gold_set: GoldSet,
    retrieved_results: Union[str, Dict, List[RetrievalResult]],
    top_k: List[int] = [1, 3, 5],
    metric_threshold: float = 0.5
) -> EvaluationResult:
    """Evaluates retrieved results against ground truth source anchors."""
    ...

def compare(
    baseline_result: EvaluationResult,
    candidate_result: EvaluationResult
) -> ComparisonResult:
    """Compares baseline and candidate evaluation results to detect regressions."""
    ...
```

---

## 20. ARCHITECTURE DESIGN (`/architecture`)

### Canonical Pipeline Visualization

```
[1. Source Docs] ──► [2. Canonicalization] ──► [3. Chunking] ──► [4. Retrieval]
                                                                        │
[8. Test Results] ◄── [7. CI Integration] ◄── [6. Metrics] ◄── [5. SPANCHOR]
```

### Interactive Pipeline Inspector Nodes
Clicking any node in the architecture diagram displays its detailed technical specification card:
- **Node 1 (Source Documents):** Raw un-chunked document repository.
- **Node 2 (Canonicalization):** Whitespace normalization, unicode normalization, character indexing.
- **Node 3 (Chunking Engine):** Variable length chunk generator (Fixed, Semantic, Sentence-level).
- **Node 4 (Retrieval Pipeline):** Vector search, BM25, or hybrid retrieval engine.
- **Node 5 (SPANCHOR Engine):** Character span matching and SHA-256 hash verification.
- **Node 6 (Metrics Calculator):** Hit@K, Recall@K, Precision@K, and IoU computation.
- **Node 7 (CI Integration):** Pytest test runner and GitHub Actions failure rules.
- **Node 8 (Test Results):** JSON reports and stdout CLI summary.

---

## 21. "WHAT SPANCHOR IS NOT"

### Explicit Boundaries & Non-Goals

| Feature / Domain | Supported by SPANCHOR? | Boundary Explanation |
|---|---|---|
| **Retrieval Regression Testing** | **YES (Core)** | Evaluates if candidate retrieval yields ground-truth evidence spans. |
| **Vector Database** | **NO** | SPANCHOR does not store embeddings or perform vector indexes. |
| **Embedding Model / Generator** | **NO** | SPANCHOR does not generate text embeddings. |
| **LLM Provider / Judge** | **NO** | SPANCHOR uses deterministic text matching, not expensive LLM judge calls. |
| **Chatbot / Agent Framework** | **NO** | SPANCHOR evaluates retrieval output, not chat response generation. |
| **PDF Parser / OCR Engine** | **NO** | Document parsing must occur prior to SPANCHOR evaluation. |
| **Hosted Cloud Service** | **NO** | SPANCHOR is an open-source, local-first Python library and CLI. |

---

## 22. DATA ARCHITECTURE

### Directory Organization
All demo data and content fixtures reside strictly in local TypeScript files under `src/data/`:

```
src/data/
├── demoDataset.ts     # CloudSync 100-query benchmark dataset
├── demoExecution.ts   # Execution simulation state machine steps
├── docsContent.ts     # Markdown content for all 12 documentation pages
├── examplesData.ts    # 6 reference code workflow examples
├── apiData.ts         # Python API class & method signatures
└── metricsData.ts     # Formula definitions and visual diagram metadata
```

### Key TypeScript Interfaces (`src/types/index.ts`)

```typescript
export interface DocumentSpan {
  doc_id: string;
  start_offset: number;
  end_offset: number;
  text_hash: string;
  canonical_text: string;
}

export interface BenchmarkQuery {
  query_id: string;
  query_text: string;
  gold_spans: DocumentSpan[];
  baseline_score: {
    recall_at_5: number;
    hit_at_5: number;
    iou: number;
  };
  candidate_score: {
    recall_at_5: number;
    hit_at_5: number;
    iou: number;
  };
  delta: number;
  status: 'IMPROVED' | 'UNCHANGED' | 'REGRESSED';
}

export interface SimulationStep {
  stepIndex: number;
  stateName: string;
  terminalLog: string;
  progressPercent: number;
  durationMs: number;
}
```

---

## 23. STATE ARCHITECTURE

### React State Management Rules
- **No Heavy Redux/Zustand Needed:** State is strictly localized using React Context and custom hooks.
- **Simulation State (`useSimulation`):** Manages state machine transitions (`IDLE` to `COMPLETE`), terminal log buffer, and progress percentage.
- **Filter State (`useTableFilter`):** Manages search string, selected status tab (`ALL`, `REGRESSED`, `IMPROVED`), and column sort key.
- **Docs Navigation State (`useDocsNav`):** Manages active route, sidebar open state (mobile), and right TOC active heading.

---

## 24. COMPONENT ARCHITECTURE

### Reusable UI Component Hierarchy

```
src/components/
├── common/
│   ├── Navbar.tsx
│   ├── Footer.tsx
│   ├── Button.tsx
│   ├── Badge.tsx
│   ├── Card.tsx
│   ├── StatusBadge.tsx
│   └── AnimatedNumber.tsx
├── simulation/
│   ├── CodeEditor.tsx
│   ├── Terminal.tsx
│   ├── ExecutionTrace.tsx
│   ├── MetricCard.tsx
│   ├── ComparisonPanel.tsx
│   └── RegressionTable.tsx
├── visualization/
│   ├── PipelineDiagram.tsx
│   ├── SourceAnchorViewer.tsx
│   ├── ArchitectureVisualizer.tsx
│   └── MetricChart.tsx
└── docs/
    ├── DocsSidebar.tsx
    ├── DocsToc.tsx
    ├── CodeBlock.tsx
    └── Callout.tsx
```

---

## 25. PROJECT STRUCTURE

```
spanchor-website/
├── public/
│   ├── favicon.svg
│   └── og-image.png
├── src/
│   ├── components/       # Reusable UI component library
│   ├── data/             # Static deterministic data fixtures
│   ├── hooks/            # React state & simulation hooks
│   ├── layouts/          # RootLayout, DocsLayout, PlaygroundLayout
│   ├── pages/            # Page components for all routes
│   ├── styles/           # Global Tailwind CSS definitions
│   ├── types/            # TypeScript type declarations
│   ├── utils/            # Helper functions (copy, formatters)
│   ├── App.tsx           # Router configuration
│   └── main.tsx          # Application entry point
├── index.html            # HTML metadata & font links
├── tailwind.config.ts    # Tailwind token overrides
├── tsconfig.json         # Strict TypeScript compiler options
└── vite.config.ts        # Vite bundle configuration
```

---

## 26. RESPONSIVE DESIGN SPECIFICATION

### Breakpoints & Layout Adaptations

| Screen Width | Target Device | Layout Behavior |
|---|---|---|
| `< 640px` | Mobile Phones | Single column vertical stack. Navbar collapses to hamburger drawer. Regression table converts to query cards. Hero visual scales down cleanly. |
| `640px - 1024px` | Tablets & Small Laptops | 2-column grids where applicable. Docs sidebar becomes a collapsible top bar or drawer. Code editor and terminal stack vertically. |
| `> 1024px` | Desktop Displays | Full multi-column split layouts. Playground displays side-by-side editor and simulation terminal. Docs display 3-column view (Nav, Content, TOC). |

### Zero Overflow Rule
All code blocks and data tables MUST use horizontal scroll wrappers (`overflow-x-auto`) to guarantee zero body page horizontal overflow (`overflow-x-hidden` on root container).

---

## 27. ACCESSIBILITY (a11y) SPECIFICATION

### Accessibility Compliance Checklist
- **Semantic HTML5:** Native `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`, `<table>`, `<button>` elements used throughout.
- **Single H1 per Page:** Every route renders exactly one `<h1>` title element.
- **Contrast Ratios:** Text to background contrast ratio passes WCAG AA minimum 4.5:1 (e.g. `#0F172A` on `#FFFFFF` = 19.5:1).
- **Focus Indicators:** All interactive elements feature visible focus rings (`focus-visible:ring-2 focus-visible:ring-sky-600`).
- **Keyboard Navigation:** Full page flow accessible via `Tab`, `Shift+Tab`, `Enter`, `Space`, and `Escape`.
- **Screen Reader ARIA Attributes:** `aria-expanded`, `aria-controls`, `aria-label`, `aria-live="polite"` for terminal logs.
- **Prefers Reduced Motion:** CSS media query `@media (prefers-reduced-motion: reduce)` disables animations and typing effects.

---

## 28. ANIMATION SYSTEM

### Motion Rules & Guidelines
- **Duration Standard:** Fast micro-interactions (150ms), standard panel transitions (300ms), step updates (400ms).
- **Easing Curve:** Standard cubic-bezier `cubic-bezier(0.16, 1, 0.3, 1)` (ease-out quint).
- **Terminal Typing Effect:** 15ms per line reveal to emulate fast CLI stdout streaming.
- **Reduced Motion Fallback:** Instantly renders terminal output and completed metric values when reduced motion is preferred by user OS settings.

---

## 29. ERROR, EMPTY & LOADING STATES

### State UI Specifications
- **404 Not Found Page:** Clean slate-900 icon, error header `"Page not found"`, description, and `"Return to Landing Page"` primary button.
- **Table Empty Filter State:** Displays search icon, `"No matching query regressions found"`, and `"Clear Filters"` button.
- **Docs Page Missing State:** Fallback message indicating section is coming soon in v0.2.0.
- **Simulation Loading State:** Terminal line spinners (`/`, `-`, `\`, `|`) and animated progress bar.

---

## 30. CONTENT STRATEGY & TERMINOLOGY

### Vocabulary Rules
- **Always Use:** `Source Anchor`, `Ground Truth Span`, `RAG Regression`, `Recall@K`, `Hit@K`, `IoU`, `Baseline`, `Candidate`, `Canonical Text`.
- **Never Use:** "Smart AI Judge", "Magic Evaluation", "Instant Fix", "Revolutionary", "World-leading", "Bulletproof".
- **Tone of Voice:** Authoritative, clear, concise, developer-centric, mathematically grounded.

---

## 31. SEO & METADATA

### Head Metadata Specs
- **Default Page Title:** `SPANCHOR — Source-Anchored RAG Retrieval Regression Testing`
- **Docs Page Title Pattern:** `{Page Title} — SPANCHOR Documentation`
- **Meta Description:** `"Source-anchored regression testing for RAG retrieval pipelines. Validate evidence retrieval accuracy across chunking and embedding changes."`
- **OpenGraph & Twitter Card:** `og:type = website`, `og:title`, `og:description`, `og:image = /og-image.png`.

---

## 32. EXTERNAL LINKS & CITATIONS

### Verified Repository & Package Links
- **GitHub Repository:** `https://github.com/Mukeshram-07/spanchor`
- **PyPI Package:** `https://pypi.org/project/spanchor/`
- **Link Placement Rules:** Header navbar (GitHub star badge + PyPI button), Hero CTAs, Documentation footer, Global footer.

---

## 33. IMPLEMENTATION ARCHITECTURE

### Tech Stack Specification
- **Framework:** React 18+ with TypeScript (Strict mode enabled)
- **Build Tool:** Vite 5+
- **Styling:** Tailwind CSS 3+ (Vanilla CSS variables + design tokens)
- **Icons:** Lucide React (`lucide-react`)
- **Animation:** Framer Motion (`framer-motion`) or lightweight CSS transitions
- **Routing:** React Router DOM v6 (`react-router-dom`)

---

## 34. IMPLEMENTATION PRINCIPLES

1. **Reusable Component Hierarchy:** Every UI pattern (badge, card, code block, table cell) MUST be a modular, typed component.
2. **Deterministic Execution:** Simulation must run in client-side TS without external APIs or backend server requirements.
3. **Strict TypeScript:** No `any` types allowed. Complete interfaces defined for all props, data structures, and state hooks.
4. **Single Source of Truth:** Data fixtures stored centrally in `src/data/`.
5. **Clean Separation of Concerns:** UI presentation layer separated from simulation hook logic.

---

## 35. TESTING & QUALITY ASSURANCE STRATEGY

### QA Testing Layers

1. **Component QA:** Verify visual rendering of buttons, badges, inputs, and modals in isolated states.
2. **Interaction QA:** Verify tab switching, copy-to-clipboard, drawer toggles, and dropdown selections.
3. **Simulation Determinism QA:** Confirm that clicking **Run** N times produces identical terminal text, metric values, and regression counts.
4. **Route QA:** Verify all 17 routes render correctly without white-screen or routing errors.
5. **Responsive QA:** Test layouts on Mobile (375px), Tablet (768px), Laptop (1024px), Desktop (1440px).
6. **Accessibility QA:** Test keyboard navigation with `Tab`, verify focus outlines, run WAVE/Lighthouse accessibility audits.
7. **Build QA:** Verify clean compilation via `npm run build` with zero TypeScript or Vite errors.
8. **Content QA:** Check for typos, broken links, and verify external GitHub/PyPI URLs.

---

## 36. PERFORMANCE STRATEGY

- **Target Bundle Size:** Core initial JS bundle `< 150KB` gzipped.
- **Route Code-Splitting:** Dynamic imports via `React.lazy()` for documentation pages and playground.
- **Re-render Optimization:** Wrap simulation data processors and table filter pipelines in `useMemo` and `useCallback`.
- **Zero Heavy Assets:** All icons are inline SVGs; no heavy raster images.

---

## 37. SECURITY & SAFETY

- **No Code Execution:** The editor displays visual code only. No user code is compiled or executed.
- **No `eval()` or `Function()`:** Zero dynamic code evaluation.
- **No Data Collection:** Zero tracking cookies, zero analytics scripts, zero third-party data transmission.
- **Local Browser Execution:** All state remains 100% inside the user's browser memory.

---

## 38. PRODUCTION BUILD STRATEGY

### Expected Build Commands
```bash
# Install dependencies
npm install

# Run local development server
npm run dev

# Run TypeScript check and production bundle
npm run build

# Preview production build locally
npm run preview
```

### Static Build Output
The production build compiles into static static assets in `dist/`, ready for deployment to static hosting platforms (GitHub Pages, Vercel, Netlify, Cloudflare Pages) with SPA route fallback (`index.html`).

---

## 39. FINAL VALIDATION CHECKLIST

### Product & UX Validation
- [x] Landing page complete with all 11 required sections.
- [x] Hero section includes interactive animated pipeline flow.
- [x] Code → Run → Terminal → Metrics simulation works deterministically.
- [x] Playground layout fully specified with split pane and table filters.
- [x] Documentation layout specified with 12 complete pages and navigation.
- [x] Examples page covers all 6 reference workflows.
- [x] Architecture page visualizes the 8-step RAG pipeline.
- [x] "What SPANCHOR Is Not" matrix clearly defines boundaries.

### Technical & Code Quality Validation
- [x] Zero task IDs (`TASK-001`, `TASK-002`) used in specification.
- [x] Light Theme Only policy strictly specified.
- [x] Zero backend dependency specified.
- [x] External GitHub and PyPI links correctly pointed to verified URLs.

---

## 40. FINAL DELIVERABLE SPECIFICATION: DEFINITION OF DONE

The finished SPANCHOR website deliverable represents a complete, polished, developer-focused frontend application.

The core signature interaction of the completed website is:

```
[ CODE EDITOR ] ──► [ RUN SIMULATION ] ──► [ TERMINAL EXECUTION ] ──► [ SOURCE ANCHORS ] ──► [ LIVE METRICS ] ──► [ REGRESSION TABLE ]
```

When fully built according to this specification, any developer visiting the website will immediately understand SPANCHOR's core innovation — source-anchored regression testing for RAG retrieval — through interactive visual proof, comprehensive documentation, and a production-grade UI design system.
