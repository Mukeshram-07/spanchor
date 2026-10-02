# SPANCHOR Frontend Website - Implementation Tasks

**Total Tasks**: 85 | **P0 Tasks**: 47 | **P1 Tasks**: 30 | **P2 Tasks**: 8

---

## 1. Implementation Strategy

The SPANCHOR website is structured around a **hero-to-demo-to-docs** funnel:

1. **Foundation** (Phase 0): Verify and establish the technical foundation
2. **Design System** (Phase 1): Build reusable UI components
3. **Simulation Engine** (Phase 2): Create deterministic demo data and simulation hooks
4. **Execution Visualization** (Phase 3): Build the CODE → RUN → METRICS centerpiece
5. **Landing Page** (Phase 4): Assemble hero, pipeline, and CTAs
6. **Source Anchors** (Phase 5): Explain and visualize source anchor concept
7. **Comparison & Regression** (Phase 6): Show baseline vs candidate analysis
8. **Documentation** (Phase 7-9): Build multi-page docs with sidebar navigation
9. **Playground & Examples** (Phase 10-11): Interactive demo and reference examples
10. **API Docs & Architecture** (Phase 12-13): Technical deep dives
11. **Polish & Testing** (Phase 14-15): Responsive design, accessibility, SEO

**Key Dependencies:**
- All phases depend on Phase 0 (Foundation)
- Phases 1-3 are prerequisites for Phases 4-6
- Documentation can branch from Phase 1
- Playground requires Phases 1-3

---

## 2. Phase Overview

| Phase | Purpose | P0 Tasks | P1 Tasks | P2 Tasks |
|-------|---------|----------|----------|----------|
| **Phase 0** | Project Foundation | 4 | 1 | 0 |
| **Phase 1** | Design System & Shared Components | 10 | 5 | 0 |
| **Phase 2** | Core Demo Data & Simulation | 6 | 3 | 0 |
| **Phase 3** | Execution Visualization | 8 | 4 | 1 |
| **Phase 4** | Landing Page | 10 | 3 | 1 |
| **Phase 5** | Source Anchors Visualization | 2 | 4 | 0 |
| **Phase 6** | Baseline/Candidate Comparison | 4 | 3 | 0 |
| **Phase 7** | Regression Table | 0 | 3 | 1 |
| **Phase 8** | Documentation Layout & Routes | 3 | 2 | 0 |
| **Phase 9** | Documentation Content | 0 | 12 | 0 |
| **Phase 10** | Playground | 3 | 2 | 0 |
| **Phase 11** | Examples | 0 | 3 | 0 |
| **Phase 12** | API Documentation | 0 | 3 | 1 |
| **Phase 13** | Architecture Page | 1 | 2 | 0 |
| **Phase 14** | Responsive Design & Testing | 2 | 1 | 1 |
| **Phase 15** | Accessibility & SEO | 2 | 2 | 2 |
| **Phase 16** | Quality Assurance | 2 | 0 | 0 |

---

## 3. Detailed Tasks

---

## PHASE 0: Project Foundation

### TASK-001 — Verify Project Setup (Vite + React + TypeScript)

**Priority:** P0  
**Requirements:** FR-102, NFR-001, NFR-002  
**Dependencies:** None  
**Objective:** Inspect and verify existing Vite + React + TypeScript configuration.

**Implementation:**
- Verify `vite.config.ts` includes React plugin
- Verify `tsconfig.json` has `"strict": true`
- Verify `package.json` has build, dev, preview scripts
- Verify `src/main.tsx` and `src/App.tsx` exist
- Check for console warnings during build

**Files/Areas:**
- `vite.config.ts`
- `tsconfig.json`
- `package.json`
- `src/main.tsx`
- `src/App.tsx`

**Acceptance Criteria:**
- [x] `npm run build` succeeds with no errors
- [x] `npm run dev` runs on localhost:5173
- [x] TypeScript strict mode is enabled
- [x] No console warnings during build
- [x] React Router is installed

**Validation:** Run `npm run build` and `npm run dev`; check no errors in console.

---

### TASK-002 — Verify Tailwind CSS Configuration

**Priority:** P0  
**Requirements:** FR-102, Design Tokens  
**Dependencies:** TASK-001  
**Objective:** Verify Tailwind CSS is properly configured with design tokens.

**Implementation:**
- Verify `tailwind.config.ts` exists and is valid
- Verify `src/index.css` has @tailwind directives
- Verify design tokens are defined:
  - Colors (primary, secondary, accent, success, warning, error, neutral)
  - Spacing scale (xs, sm, md, lg, xl, 2xl, 3xl, 4xl)
  - Border radius (sm, md, lg, full)
  - Shadows (sm, md, lg)
  - Typography (font families)
- Verify `src/main.tsx` imports `src/index.css`

**Files/Areas:**
- `tailwind.config.ts`
- `src/index.css`
- `src/main.tsx`

**Acceptance Criteria:**
- [x] Tailwind compiles without errors
- [x] Custom colors are available in components
- [x] Design tokens match specification
- [~] No console errors or warnings

**Validation:** Create test component using custom colors; verify in browser.

---

### TASK-003 — Install Required Dependencies

**Priority:** P0  
**Requirements:** FR-102, FR-082  
**Dependencies:** TASK-001  
**Objective:** Verify all required libraries are installed.

**Implementation:**
- Verify installed: `react-router-dom`, `framer-motion`, `lucide-react`
- Verify installed: `highlight.js` (for code syntax highlighting)
- Check `package.json` for exact versions
- Run `npm install` to ensure clean install

**Files/Areas:**
- `package.json`
- `node_modules/`

**Acceptance Criteria:**
- [~] All required dependencies installed
- [~] No peer dependency warnings
- [~] No security vulnerabilities (run `npm audit`)
- [~] `npm run build` succeeds

**Validation:** Run `npm list` and verify all packages present; run `npm audit`.

---

### TASK-004 — Establish Routing & File Structure

**Priority:** P0  
**Requirements:** FR-042, FR-066  
**Dependencies:** TASK-001  
**Objective:** Set up React Router configuration and file structure.

**Implementation:**
- Create `src/App.tsx` with BrowserRouter and route skeleton:
  - `/` → Home
  - `/docs/*` → Docs layout
  - `/playground` → Playground
  - `/examples` → Examples
  - `/api` → API docs
  - `/architecture` → Architecture
  - `*` → 404
- Create directory structure:
  ```
  src/
  ├── components/
  │   ├── layouts/ (Navbar, Footer, DocsSidebar)
  │   ├── ui/ (Button, Badge, Card, etc.)
  │   ├── features/ (HeroSection, Terminal, etc.)
  │   └── docs/ (placeholder)
  ├── pages/ (Home, NotFound, Playground, Examples, etc.)
  ├── hooks/ (useSimulation, useAnimatedMetric, etc.)
  ├── data/ (demoData, docsContent, examples, apiDocs)
  ├── types/ (TypeScript interfaces)
  ├── utils/ (animations, cn utility)
  └── styles/ (additional CSS if needed)
  ```
- Create placeholder page files (content to be filled in later)

**Files/Areas:**
- `src/App.tsx`
- `src/main.tsx`
- All directories listed above
- Placeholder page files

**Acceptance Criteria:**
- [~] All routes are accessible
- [~] URL updates on navigation
- [~] Browser back/forward work
- [~] 404 page displays for unknown routes
- [~] TypeScript has no errors

**Validation:** Navigate to each route in browser; check URL bar changes correctly.

---

### TASK-005 — Create Animation Utilities

**Priority:** P1  
**Requirements:** FR-082, FR-083, FR-084  
**Dependencies:** TASK-002  
**Objective:** Create reusable Framer Motion animation variants.

**Implementation:**
- Create `src/utils/animations.ts` with animation variants:
  - `fadeIn` (opacity 0 → 1)
  - `slideUp` (y transform + fade)
  - `slideDown` (y transform + fade)
  - `slideLeft` (x transform + fade)
  - `slideRight` (x transform + fade)
  - `scaleIn` (scale 0 → 1 + fade)
  - `staggerContainer` (stagger children)
  - `pulseAnimation` (loop pulse effect)
  - `countUp` (numeric animation)
- Ensure all animations respect `prefers-reduced-motion`

**Files/Areas:**
- `src/utils/animations.ts`

**Acceptance Criteria:**
- [~] All animation variants work
- [~] Animations can be imported and used
- [~] No TypeScript errors
- [~] Reduced motion is respected

**Validation:** Create test component using each animation variant; visually verify in browser.

---

## PHASE 1: Design System & Shared Components

### TASK-010 — Create Button Component

**Priority:** P0  
**Requirements:** FR-004, FR-005, FR-066  
**Dependencies:** TASK-002, TASK-005  
**Objective:** Build reusable Button component with variants and states.

**Implementation:**
- Create `src/components/ui/Button.tsx`
- Variants: `primary`, `secondary`, `ghost`, `danger`
- Sizes: `sm`, `md`, `lg`
- States: `disabled`, `loading`
- Props: `onClick`, `children`, `className`, `type`, `href` (for links)
- Include:
  - Proper TypeScript types
  - ARIA labels
  - Focus states
  - Hover states
  - Disabled state styling
- Use Tailwind design tokens

**Files/Areas:**
- `src/components/ui/Button.tsx`

**Acceptance Criteria:**
- [~] All variants render correctly
- [~] All sizes render correctly
- [~] Disabled state works
- [~] Loading state shows spinner/indicator
- [~] Hover and focus states are visible
- [~] ARIA labels present
- [~] TypeScript strict mode passes

**Validation:** Create test component with all button variants; visually verify all states.

---

### TASK-011 — Create Badge Component

**Priority:** P0  
**Requirements:** FR-003  
**Dependencies:** TASK-002  
**Objective:** Build Badge component for tech badges and status indicators.

**Implementation:**
- Create `src/components/ui/Badge.tsx`
- Variants: `tech`, `status`, `success`, `warning`, `error`
- Props: `children`, `variant`, `className`
- Support `tech` variant: displays "Python • Local-first • Deterministic"
- Support `status` variant: displays with color coding
- Use Tailwind design tokens for colors
- Professional, minimal styling

**Files/Areas:**
- `src/components/ui/Badge.tsx`

**Acceptance Criteria:**
- [~] Tech badge displays correctly
- [~] Status badge displays with color
- [~] All variants render
- [~] Styling is professional and minimal
- [~] TypeScript passes

**Validation:** Render tech badge with "Python • Local-first • Deterministic"; verify styling.

---

### TASK-012 — Create Card Component

**Priority:** P0  
**Requirements:** FR-023, Design System  
**Dependencies:** TASK-002  
**Objective:** Build generic reusable Card component.

**Implementation:**
- Create `src/components/ui/Card.tsx`
- Props: `children`, `className`, `variant` (default, hover, shadow)
- Includes:
  - Proper padding and spacing
  - Subtle border or shadow
  - Hover effects (if variant specified)
  - Professional styling
- Use Tailwind design tokens

**Files/Areas:**
- `src/components/ui/Card.tsx`

**Acceptance Criteria:**
- [~] Card renders with proper spacing
- [~] Hover effects work (if enabled)
- [~] Styling is professional
- [ ] TypeScript passes

**Validation:** Create multiple cards with different content; verify spacing and hover.

---

### TASK-013 — Create StatusIndicator Component

**Priority:** P0  
**Requirements:** FR-010  
**Dependencies:** TASK-002  
**Objective:** Build component for displaying ✓, ⚠, ✗ status indicators.

**Implementation:**
- Create `src/components/ui/StatusIndicator.tsx`
- Types: `success` (✓), `warning` (⚠), `error` (✗)
- Props: `status`, `size` (sm, md, lg), `label`
- Colors:
  - Success: green (#00AA00)
  - Warning: orange (#FF9900)
  - Error: red (#CC0000)
- Accessible: proper ARIA labels

**Files/Areas:**
- `src/components/ui/StatusIndicator.tsx`

**Acceptance Criteria:**
- [~] All status types render
- [~] All sizes work
- [~] Colors match design tokens
- [ ] ARIA labels present
- [ ] TypeScript passes

**Validation:** Render all status types in all sizes; verify colors and labels.

---

### TASK-014 — Create Modal Component

**Priority:** P1  
**Requirements:** Design System  
**Dependencies:** TASK-010, TASK-002  
**Objective:** Build Modal dialog component with overlay.

**Implementation:**
- Create `src/components/ui/Modal.tsx`
- Props: `isOpen`, `onClose`, `children`, `title`, `size`
- Features:
  - Overlay/backdrop
  - Close button (X)
  - Keyboard close (ESC key)
  - Scroll lock (prevent body scroll)
  - Portal rendering (or similar)
- Use Framer Motion for animation
- Accessible: proper ARIA labels, focus management

**Files/Areas:**
- `src/components/ui/Modal.tsx`

**Acceptance Criteria:**
- [~] Modal renders when isOpen is true
- [~] Close button works
- [~] Backdrop click closes (optional)
- [~] ESC key closes
- [~] Body scroll is locked
- [~] Animation is smooth
- [ ] ARIA labels present

**Validation:** Create modal with content; test all close methods.

---

### TASK-015 — Create Drawer Component

**Priority:** P0  
**Requirements:** FR-066 (mobile navigation)  
**Dependencies:** TASK-010, TASK-005  
**Objective:** Build mobile-friendly Drawer/Sidebar component.

**Implementation:**
- Create `src/components/ui/Drawer.tsx`
- Props: `isOpen`, `onClose`, `children`, `side` (left/right)
- Features:
  - Slides in from side
  - Overlay/backdrop
  - Close button
  - Can contain navigation links
  - Smooth Framer Motion animation
  - Responsive: full-height on mobile, side-width on desktop
- Accessible: proper ARIA labels, focus trap

**Files/Areas:**
- `src/components/ui/Drawer.tsx`

**Acceptance Criteria:**
- [~] Drawer slides in smoothly
- [ ] Close button works
- [~] Backdrop click closes
- [~] Overlay is present
- [ ] Animation is smooth
- [ ] ARIA labels present

**Validation:** Open drawer; verify animation and closing.

---

### TASK-016 — Create CodeBlock Component

**Priority:** P0  
**Requirements:** FR-007, FR-059  
**Dependencies:** TASK-002  
**Objective:** Build syntax-highlighted code display component.

**Implementation:**
- Create `src/components/ui/CodeBlock.tsx`
- Features:
  - Syntax highlighting (highlight.js)
  - Line numbers
  - Copy button (with feedback)
  - Optional reset button
  - Read-only (no editing in demo)
  - Monospace font, light background
  - Mobile responsive (horizontal scroll if needed)
- Props: `code`, `language`, `title`, `showReset`, `onReset`
- Use highlight.js for syntax highlighting

**Files/Areas:**
- `src/components/ui/CodeBlock.tsx`

**Acceptance Criteria:**
- [~] Code displays with syntax highlighting
- [~] Line numbers appear
- [~] Copy button works
- [~] Copy shows feedback (e.g., "Copied!")
- [~] Reset button works (if present)
- [~] Professional appearance
- [~] Mobile responsive

**Validation:** Display Python code; test copy and reset buttons.

---

### TASK-017 — Create Navbar Component

**Priority:** P0  
**Requirements:** FR-066, FR-067, FR-068, FR-069, FR-070  
**Dependencies:** TASK-010, TASK-015, TASK-002  
**Objective:** Build sticky navigation bar with responsive mobile menu.

**Implementation:**
- Create `src/components/layouts/Navbar.tsx`
- Layout:
  - Left: SPANCHOR logo + descriptor
  - Center (desktop only): Navigation links
  - Right (desktop only): GitHub and PyPI buttons
  - Mobile: Hamburger menu → Drawer
- Links: Home, Docs, Playground, Examples, API, Architecture
- External buttons:
  - GitHub: https://github.com/Mukeshram-07/spanchor (target="_blank")
  - PyPI: https://pypi.org/project/spanchor/ (target="_blank")
- Features:
  - Sticky positioning (top: 0)
  - White background with subtle shadow
  - Active link highlighting (using useLocation)
  - Responsive: hamburger on mobile (<768px)
  - Logo navigates to home (/)

**Files/Areas:**
- `src/components/layouts/Navbar.tsx`

**Acceptance Criteria:**
- [~] Navbar is sticky
- [~] Logo navigates to home
- [~] All links navigate correctly
- [~] Active link is highlighted
- [~] GitHub/PyPI buttons open in new tab
- [~] Mobile hamburger shows on small screens
- [~] Drawer opens/closes
- [ ] Professional appearance

**Validation:** Test all links; verify sticky behavior; test mobile menu.

---

### TASK-018 — Create Footer Component

**Priority:** P0  
**Requirements:** FR-098, FR-099  
**Dependencies:** TASK-010, TASK-002  
**Objective:** Build footer with branding and links.

**Implementation:**
- Create `src/components/layouts/Footer.tsx`
- Content:
  - SPANCHOR branding and descriptor
  - Links: Docs, GitHub, PyPI, Examples, API
  - Metadata: Apache-2.0 license, Python 3.11-3.13 support
  - Auto-updating copyright year
- Layout:
  - 3-column or responsive grid
  - Light background, subtle borders
  - Professional styling
- Mobile responsive (stack vertically)

**Files/Areas:**
- `src/components/layouts/Footer.tsx`

**Acceptance Criteria:**
- [~] Footer appears at bottom
- [~] All links are clickable
- [~] External links open in new tab
- [~] License and Python versions displayed
- [~] Copyright year auto-updates
- [~] Responsive on all devices
- [ ] Professional appearance

**Validation:** Verify all links; check responsive layout on mobile.

---

### TASK-019 — Create Typography & Spacing Utilities

**Priority:** P1  
**Requirements:** Design System  
**Dependencies:** TASK-002, TASK-005  
**Objective:** Create utility components and CSS classes for typography and spacing.

**Implementation:**
- Create `src/components/ui/Typography.tsx` with:
  - `H1`, `H2`, `H3`, `H4`, `H5`, `H6` components
  - `Body`, `BodySmall`, `BodyLarge` components
  - `Mono` component for monospace text
- Verify `src/index.css` has proper Tailwind utilities
- Ensure consistent spacing via Tailwind scale

**Files/Areas:**
- `src/components/ui/Typography.tsx`
- `src/index.css`

**Acceptance Criteria:**
- [~] All typography components render
- [~] Spacing is consistent
- [~] Professional hierarchy
- [ ] TypeScript passes

**Validation:** Create page using all typography components; verify hierarchy.

---

### TASK-020 — Create Utility Functions (cn, animations)

**Priority:** P1  
**Requirements:** Design System  
**Dependencies:** TASK-002, TASK-005  
**Objective:** Create utility functions for class merging and animations.

**Implementation:**
- Create or verify `src/utils/cn.ts` (classname merge utility)
- Verify `src/utils/animations.ts` has all animation variants
- Create `src/utils/hooks.ts` for shared hook utilities (if needed)
- Ensure proper TypeScript types

**Files/Areas:**
- `src/utils/cn.ts`
- `src/utils/animations.ts`
- `src/utils/hooks.ts` (optional)

**Acceptance Criteria:**
- [~] All utilities are exported
- [~] Utilities work correctly
- [ ] TypeScript passes
- [~] No circular dependencies

**Validation:** Import and use utilities in test component.

---

## PHASE 2: Core Demo Data & Simulation Engine

### TASK-030 — Create TypeScript Interfaces & Types

**Priority:** P0  
**Requirements:** FR-104, FR-105, FR-106, FR-015, FR-016  
**Dependencies:** TASK-004  
**Objective:** Define all TypeScript types for demo data and simulation.

**Implementation:**
- Create `src/types/index.ts` with interfaces:
  - `Document` (id, name, content, metadata)
  - `Anchor` (document, startOffset, endOffset, hash, text)
  - `Span` (startOffset, endOffset, text)
  - `Query` (id, text, gold_anchors)
  - `RetrievalResult` (query_id, retrieved_spans)
  - `EvaluationResult` (query_id, metric_scores, regression_status)
  - `SimulationStep` (type, timestamp, payload)
  - `SimulationState` (isRunning, currentStep, stepData, progress)
  - `DemoDataset` (name, documents, queries, baseline, candidate)
  - `Metrics` (recall_at_5, precision_at_5, hit_at_5)

**Files/Areas:**
- `src/types/index.ts`

**Acceptance Criteria:**
- [~] All interfaces defined
- [~] Types are strictly typed
- [~] No `any` types used
- [~] TypeScript passes strict mode

**Validation:** Import types in test file; verify no errors.

---

### TASK-031 — Create Deterministic Demo Data

**Priority:** P0  
**Requirements:** FR-104, FR-105, FR-106, FR-016  
**Dependencies:** TASK-030  
**Objective:** Create all deterministic demo data that will be used throughout the app.

**Implementation:**
- Create `src/data/demoData.ts` with:
  - `DEMO_DATASET` constant:
    - name: "CloudSync Demo"
    - documents: 4 sample documents (CloudSync deployment guide, etc.)
    - queries: 100 sample queries
    - baseline metrics: Recall@5=0.405, Precision@5=0.020, Hit@5=0.410
    - candidate metrics: Recall@5=0.249, Precision@5=0.017, Hit@5=0.260
    - outcomes: Improved=6, Unchanged=75, Regressed=19
  - `EXECUTION_STEPS` array with all simulation steps
  - Document sample data (CloudSync guide excerpt, etc.)
  - Source anchor examples
  - Query and retrieval result samples

**Files/Areas:**
- `src/data/demoData.ts`

**Acceptance Criteria:**
- [~] All demo data exported
- [~] Data is strictly typed
- [~] Metrics match specification exactly
- [~] Data is deterministic (identical on every run)
- [ ] TypeScript passes

**Validation:** Import demoData; verify all metrics and counts match spec.

---

### TASK-032 — Create Documentation Content Data

**Priority:** P1  
**Requirements:** FR-045 through FR-056  
**Dependencies:** TASK-030  
**Objective:** Create content data for all documentation pages.

**Implementation:**
- Create `src/data/docsContent.ts` with:
  - Documentation for each page: intro, installation, quickstart, concepts, anchors, gold-sets, metrics, comparison, adapters, CLI, testing, limitations
  - Structured as `{ [route]: { title, description, content, sections } }`
  - Content should be markdown or structured for rendering

**Files/Areas:**
- `src/data/docsContent.ts`

**Acceptance Criteria:**
- [~] All documentation content defined
- [~] Content is accurate to SPANCHOR
- [~] Structured for easy rendering
- [ ] TypeScript passes

**Validation:** Import and verify all doc content is present.

---

### TASK-033 — Create Examples Data

**Priority:** P1  
**Requirements:** FR-058, FR-059  
**Dependencies:** TASK-030  
**Objective:** Create 6 code examples with descriptions and expected outputs.

**Implementation:**
- Create `src/data/examples.ts` with 6 examples:
  1. Basic Evaluation
  2. Baseline vs Candidate
  3. Source Anchors
  4. LangChain Adapter
  5. LlamaIndex Adapter
  6. Gold Set Import
- Each example has: `{ title, description, code, expectedOutput, language }`

**Files/Areas:**
- `src/data/examples.ts`

**Acceptance Criteria:**
- [~] All 6 examples defined
- [~] Code is syntax-highlighted-ready
- [~] Descriptions are clear
- [~] Expected outputs are realistic
- [ ] TypeScript passes

**Validation:** Import and verify all examples render correctly.

---

### TASK-034 — Create API Documentation Data

**Priority:** P1  
**Requirements:** FR-060, FR-061, FR-062  
**Dependencies:** TASK-030  
**Objective:** Create API documentation for major concepts and functions.

**Implementation:**
- Create `src/data/apiDocs.ts` with:
  - Document (class/interface docs)
  - Anchor (class/interface docs)
  - Span (class/interface docs)
  - RetrievalResult (class/interface docs)
  - EvaluationResult (class/interface docs)
  - evaluate() function
  - compare() function
- Each item has: `{ name, type, signature, parameters, returns, description, example }`

**Files/Areas:**
- `src/data/apiDocs.ts`

**Acceptance Criteria:**
- [~] All major items documented
- [~] Signatures are accurate
- [~] Examples are provided
- [ ] TypeScript passes

**Validation:** Import and verify all API docs render.

---

### TASK-035 — Implement useSimulation Hook

**Priority:** P0  
**Requirements:** FR-015, FR-016, FR-014  
**Dependencies:** TASK-031, TASK-005  
**Objective:** Create core simulation engine hook for executing demo steps.

**Implementation:**
- Create `src/hooks/useSimulation.ts`
- Hook provides:
  - `isRunning`: boolean
  - `currentStep`: number
  - `stepData`: current step payload
  - `progress`: 0-100%
  - `results`: accumulated results
  - `startSimulation()`: begin execution
  - `stopSimulation()`: stop execution
  - `resetSimulation()`: reset to initial state
- Features:
  - Advances through EXECUTION_STEPS based on timestamps
  - Properly typed with TypeScript
  - Supports multiple independent simulations
  - Complete cleanup on unmount (no memory leaks)
  - Respects component lifecycle

**Files/Areas:**
- `src/hooks/useSimulation.ts`

**Acceptance Criteria:**
- [~] Hook provides all required state
- [~] startSimulation() advances steps correctly
- [~] Timings are accurate
- [~] No memory leaks on unmount
- [~] Multiple independent instances work
- [ ] TypeScript passes

**Validation:** Create test component using hook; verify step progression and timing.

---

### TASK-036 — Implement useAnimatedMetric Hook

**Priority:** P0  
**Requirements:** FR-012, FR-084  
**Dependencies:** TASK-005, TASK-030  
**Objective:** Create hook for animating metrics from 0 to target value.

**Implementation:**
- Create `src/hooks/useAnimatedMetric.ts`
- Hook provides:
  - `displayValue`: animated number for rendering
  - `isAnimating`: boolean state
  - `startAnimation(targetValue, duration?, easing?)`: start animation
- Features:
  - Smooth animation using requestAnimationFrame
  - Configurable duration (default 1500ms) and easing
  - Respects prefers-reduced-motion (instant transition)
  - Proper TypeScript types
  - Can be triggered multiple times

**Files/Areas:**
- `src/hooks/useAnimatedMetric.ts`

**Acceptance Criteria:**
- [~] Metrics animate smoothly from 0 to target
- [~] Respects prefers-reduced-motion
- [~] Duration and easing customizable
- [~] displayValue updates during animation
- [~] No jank or stuttering
- [ ] TypeScript passes

**Validation:** Create test component; verify smooth animation.

---

### TASK-037 — Implement useExecutionTrace Hook

**Priority:** P1  
**Requirements:** FR-019, FR-083  
**Dependencies:** TASK-005, TASK-030  
**Objective:** Create hook for terminal line-by-line animation.

**Implementation:**
- Create `src/hooks/useExecutionTrace.ts`
- Hook provides:
  - `visibleLines`: array of currently visible lines
  - `currentLineIndex`: number of lines shown
  - `isRunning`: boolean state
  - `startTrace()`: begin animation
  - `stopTrace()`: stop animation
  - `resetTrace()`: reset to start
- Features:
  - Lines appear sequentially (100-200ms delay per line)
  - Respects prefers-reduced-motion (shows all immediately)
  - Proper TypeScript types
  - Can be triggered multiple times independently

**Files/Areas:**
- `src/hooks/useExecutionTrace.ts`

**Acceptance Criteria:**
- [~] Lines appear sequentially with delay
- [~] Delays are consistent
- [~] Can be stopped/reset
- [~] Multiple traces run independently
- [ ] Respects prefers-reduced-motion
- [ ] TypeScript passes

**Validation:** Create test component; verify sequential line appearance.

---

## PHASE 3: Execution Visualization

### TASK-040 — Create Terminal Component

**Priority:** P0  
**Requirements:** FR-018, FR-019, FR-031  
**Dependencies:** TASK-016, TASK-037  
**Objective:** Build terminal-style output panel with line animation.

**Implementation:**
- Create `src/components/features/Terminal.tsx`
- Features:
  - Monospace font, high-contrast styling
  - Terminal-like appearance (dark background or light with contrast)
  - Displays: `$ spanchor evaluate` prompt
  - Accepts array of terminal lines
  - Animates lines sequentially using `useExecutionTrace`
  - Shows ✓ (success) and ⚠ (warning) symbols
  - Ends with: `$ done`
- Props: `lines`, `isAnimating`, `onComplete`
- Mobile responsive (horizontal scroll if needed)

**Files/Areas:**
- `src/components/features/Terminal.tsx`

**Acceptance Criteria:**
- [~] Terminal displays with correct styling
- [~] Lines animate sequentially
- [~] Symbols display correctly
- [~] High contrast and readable
- [ ] Mobile responsive
- [~] Animation respects prefers-reduced-motion
- [ ] TypeScript passes

**Validation:** Render terminal with demo lines; verify animation.

---

### TASK-041 — Create MetricsDisplay Component

**Priority:** P0  
**Requirements:** FR-012, FR-084  
**Dependencies:** TASK-036, TASK-012  
**Objective:** Build animated metrics display component.

**Implementation:**
- Create `src/components/features/MetricsDisplay.tsx`
- Displays metrics:
  - Recall@5: 0.405
  - Precision@5: 0.020
  - Hit@5: 0.410
  - Regressions: 19
  - Improved: 6
  - Unchanged: 75
- Features:
  - Uses `useAnimatedMetric` for each value
  - Grid or column layout
  - Professional formatting (decimal places, counts)
  - Mobile responsive
- Props: `isAnimating`, `metrics`

**Files/Areas:**
- `src/components/features/MetricsDisplay.tsx`

**Acceptance Criteria:**
- [~] All metrics display
- [~] Values animate from 0 to final
- [ ] Animation is smooth
- [~] Layout is responsive
- [ ] Professional appearance
- [ ] TypeScript passes

**Validation:** Render with demo data; verify animation.

---

### TASK-042 — Create QueryProgressList Component

**Priority:** P0  
**Requirements:** FR-010  
**Dependencies:** TASK-013, TASK-037  
**Objective:** Build component showing query processing progress.

**Implementation:**
- Create `src/components/features/QueryProgressList.tsx`
- Displays queries: "Query 001 ✓ Query 002 ✓ Query 003 ⚠ ..."
- Features:
  - Uses StatusIndicator for each query status
  - Animates queries appearing sequentially
  - Shows subset (e.g., first 20-30 queries visible, scroll for more)
  - Scrollable if many queries
  - Professional layout
- Props: `queries`, `isAnimating`

**Files/Areas:**
- `src/components/features/QueryProgressList.tsx`

**Acceptance Criteria:**
- [~] Queries display with status
- [~] Animation is sequential
- [~] Layout works on mobile
- [~] Scrollable if needed
- [ ] Professional appearance
- [ ] TypeScript passes

**Validation:** Render with demo queries; verify animation.

---

### TASK-043 — Create ExecutionOutput Component

**Priority:** P0  
**Requirements:** FR-009, FR-010, FR-013  
**Dependencies:** TASK-040, TASK-041, TASK-042, TASK-012  
**Objective:** Build large output visualization panel combining Terminal, Metrics, and Query Progress.

**Implementation:**
- Create `src/components/features/ExecutionOutput.tsx`
- Structure:
  - Title: "SPANCHOR RUN"
  - Status field: "READY" → "RUNNING" → "COMPLETE"
  - Tabbed content area or stacked sections:
    - Tab 1: Query Progress
    - Tab 2: Terminal Output
    - Tab 3: Metrics & Summary
- Props: `simulationState`, `selectedTab`, `onTabChange`
- Features:
  - Responsive layout
  - Professional styling
  - Status updates correctly

**Files/Areas:**
- `src/components/features/ExecutionOutput.tsx`

**Acceptance Criteria:**
- [~] Component renders without errors
- [~] Status updates correctly
- [~] Tabs/sections work
- [~] Content displays properly
- [~] Responsive design
- [ ] Professional appearance
- [ ] TypeScript passes

**Validation:** Render with simulation state; test tab switching.

---

### TASK-044 — Create Run Button & Simulation Trigger

**Priority:** P0  
**Requirements:** FR-008, FR-014  
**Dependencies:** TASK-010, TASK-035  
**Objective:** Create Run button that triggers simulation.

**Implementation:**
- Create `src/components/features/RunButton.tsx` or integrate into ActionSection
- Features:
  - Button text: "▶ Run Evaluation"
  - On click, changes to "Running..."
  - Triggers `useSimulation().startSimulation()`
  - After simulation ends, reverts to "▶ Run Evaluation"
  - Can be clicked again to replay
- Props: `onRun`, `isRunning`

**Files/Areas:**
- `src/components/features/RunButton.tsx` (or integrated component)

**Acceptance Criteria:**
- [~] Button text is correct
- [~] Button triggers simulation
- [~] Loading state shows
- [~] Can be clicked multiple times
- [~] Reverts after simulation
- [ ] TypeScript passes

**Validation:** Click button; verify simulation starts and completes.

---

### TASK-045 — Create ActionSection (Code + Run + Output)

**Priority:** P0  
**Requirements:** FR-007 through FR-014  
**Dependencies:** TASK-016, TASK-043, TASK-044, TASK-035  
**Objective:** Assemble the split-layout demo: Code → Run → Visualization.

**Implementation:**
- Create `src/components/features/ActionSection.tsx`
- Layout:
  - Left column (desktop) / Top (mobile): CodeBlock with Python code
  - Below code: Run button
  - Right column (desktop) / Below (mobile): ExecutionOutput
- Features:
  - Manages shared simulation state using `useSimulation`
  - Run button triggers `startSimulation()`
  - ExecutionOutput receives simulation state
  - Responsive: side-by-side on desktop, stacked on mobile
  - Professional layout and spacing

**Files/Areas:**
- `src/components/features/ActionSection.tsx`

**Acceptance Criteria:**
- [~] Layout is split on desktop, stacked on mobile
- [~] Code editor displays Python code
- [~] Run button works
- [~] ExecutionOutput updates during simulation
- [~] Terminal animates line-by-line
- [~] Metrics animate
- [ ] Professional appearance
- [ ] Responsive design
- [ ] TypeScript passes

**Validation:** Render section; click Run button; verify entire flow works.

---

### TASK-046 — Add Execution Simulation Data

**Priority:** P1  
**Requirements:** FR-015, FR-016  
**Dependencies:** TASK-031, TASK-035  
**Objective:** Populate EXECUTION_STEPS with all simulation step data.

**Implementation:**
- Update `src/data/demoData.ts` with complete EXECUTION_STEPS array:
  - Step 1: "Loading gold set..." (type: status)
  - Step 2: "✓ 100 queries loaded" (type: status)
  - Step 3-22: Query processing (type: query, payload: {queryId, status})
  - Step 23: "Computing metrics..." (type: status)
  - Step 24-26: Metrics (type: metric, payload: {name, value})
  - Step 27: "Regression analysis complete." (type: status)
  - Step 28: "19 regressions detected." (type: status)
  - Step 29: Summary (type: summary, payload: outcomes)
- Each step has a `timestamp` (relative timing in ms)
- All data is deterministic

**Files/Areas:**
- `src/data/demoData.ts`

**Acceptance Criteria:**
- [~] All steps defined
- [~] Timestamps are in order
- [~] Data matches simulation requirements
- [~] Deterministic (same every run)
- [ ] TypeScript passes

**Validation:** Import and verify all steps are present and ordered.

---

### TASK-047 — Test Simulation End-to-End

**Priority:** P1  
**Requirements:** FR-014, FR-016  
**Dependencies:** TASK-045, TASK-046  
**Objective:** Verify the complete CODE → RUN → VISUALIZATION flow works.

**Implementation:**
- Create test page or use Playground
- Render ActionSection
- Click Run button
- Observe:
  - Terminal animates lines sequentially
  - Query progress shows sequentially
  - Metrics animate from 0 to final values
  - Status updates correctly
  - Simulation completes
  - Results are deterministic (run multiple times, get identical results)

**Files/Areas:**
- Test component or page

**Acceptance Criteria:**
- [~] Simulation starts on button click
- [~] Terminal animates correctly
- [~] Query progress animates correctly
- [~] Metrics animate correctly
- [~] Simulation completes
- [~] Results are identical on multiple runs (deterministic)
- [~] No console errors

**Validation:** Render ActionSection; click Run multiple times; verify determinism.

---

## PHASE 4: Landing Page

### TASK-050 — Create HeroSection Component

**Priority:** P0  
**Requirements:** FR-001, FR-002, FR-003, FR-004, FR-005, FR-006  
**Dependencies:** TASK-010, TASK-011, TASK-002, TASK-005  
**Objective:** Build hero section with headline, subheadline, badge, and CTAs.

**Implementation:**
- Create `src/components/features/HeroSection.tsx`
- Content:
  - Headline: "Regression testing for RAG retrieval."
  - Subheadline: "Validate whether your retrieval pipeline still finds the evidence it needs — using stable source anchors instead of fragile chunk IDs."
  - Technical badge: "Python • Local-first • Deterministic"
  - Primary CTA: "Try Interactive Demo" (scrolls to #action-section or navigates)
  - Secondary CTA: "Read Documentation" (navigates to /docs)
- Features:
  - Centered layout
  - Professional typography
  - Smooth Framer Motion animations
  - Responsive (mobile stacked buttons, desktop side-by-side)
  - Decorative background elements (gradient blobs, subtle animations)
  - Respects prefers-reduced-motion
- Props: `onDemoClick` (callback for demo scroll/nav)

**Files/Areas:**
- `src/components/features/HeroSection.tsx`

**Acceptance Criteria:**
- [~] All text displays correctly
- [~] CTAs are clickable
- [~] Badge visible and styled
- [ ] Layout is responsive
- [~] Animations are smooth
- [ ] Professional appearance
- [ ] TypeScript passes

**Validation:** Render section; verify all text and buttons visible and functional.

---

### TASK-051 — Create PipelineVisualization Component

**Priority:** P0  
**Requirements:** FR-006, FR-082  
**Dependencies:** TASK-002, TASK-005, TASK-002  
**Objective:** Build animated pipeline diagram showing data flow through 5 stages.

**Implementation:**
- Create `src/components/features/PipelineVisualization.tsx`
- Pipeline stages (5):
  1. Question: "What caused the deployment failure?"
  2. Retriever: Icon and label
  3. Retrieved Evidence: 3 evidence cards with confidence scores
  4. SPANCHOR: Icon and label
  5. Regression Result: Metrics display
- Features:
  - Smooth animation (2-3 seconds total)
  - Data flows top-to-bottom or left-to-right
  - Evidence cards appear with text
  - Final results show: Recall@5 (0.405), Hit@5 (0.410), Regressions (19)
  - Auto-loop with scroll trigger (IntersectionObserver)
  - Respects prefers-reduced-motion
  - Framer Motion for all animations
  - Responsive (vertical on mobile, horizontal on desktop)
- Props: `onComplete` (optional callback)

**Files/Areas:**
- `src/components/features/PipelineVisualization.tsx`

**Acceptance Criteria:**
- [~] Pipeline stages display
- [~] Animation is smooth and professional
- [~] Data flows through sequentially
- [~] Evidence cards appear and disappear
- [~] Results display at end
- [~] Auto-loops or restarts on interaction
- [ ] Respects prefers-reduced-motion
- [ ] Mobile responsive
- [ ] TypeScript passes

**Validation:** Render component; observe full animation cycle; verify mobile layout.

---

### TASK-052 — Create PlaceholderSection Component

**Priority:** P1  
**Requirements:** FR-020, FR-025, Design System  
**Dependencies:** TASK-002, TASK-005  
**Objective:** Create reusable placeholder section component for future content.

**Implementation:**
- Create `src/components/features/PlaceholderSection.tsx`
- Props: `id`, `title`, `description`
- Features:
  - Centered layout
  - Title and description
  - Placeholder content area
  - Fade-in animation on scroll
  - Professional styling
- Used for sections that will be filled in later phases

**Files/Areas:**
- `src/components/features/PlaceholderSection.tsx`

**Acceptance Criteria:**
- [~] Component renders
- [~] Animations work
- [~] Responsive layout
- [ ] Professional appearance
- [ ] TypeScript passes

**Validation:** Render with test content; verify animation.

---

### TASK-053 — Create Home Page

**Priority:** P0  
**Requirements:** FR-001 through FR-006  
**Dependencies:** TASK-050, TASK-051, TASK-045, TASK-017, TASK-018, TASK-052  
**Objective:** Assemble the complete home page with all sections.

**Implementation:**
- Update `src/pages/Home.tsx`
- Structure:
  1. Navbar (layout wrapper)
  2. HeroSection
  3. PipelineVisualization
  4. ActionSection (Code → Run → Output)
  5. PlaceholderSection: "Why source anchors?"
  6. PlaceholderSection: "Detect retrieval regressions"
  7. PlaceholderSection: "How SPANCHOR works"
  8. Footer (layout wrapper)
- Features:
  - Professional spacing between sections
  - Section dividers (subtle borders)
  - Smooth scrolling
  - Responsive on all devices
  - No horizontal overflow

**Files/Areas:**
- `src/pages/Home.tsx`

**Acceptance Criteria:**
- [~] Page renders without errors
- [~] All sections visible
- [~] Responsive on mobile, tablet, desktop
- [~] Navigation and footer present
- [~] Sections are visually distinct
- [~] Professional spacing
- [ ] No console errors
- [ ] TypeScript passes

**Validation:** Render home page; scroll through all sections; test on mobile.

---

### TASK-054 — Verify Landing Page & Demo Flow

**Priority:** P0  
**Requirements:** FR-001 through FR-014  
**Dependencies:** TASK-053  
**Objective:** End-to-end test of landing page and demo flow.

**Implementation:**
- Load home page
- Verify hero section is visible and engaging
- Click "Try Interactive Demo" → scrolls to ActionSection
- Click "Read Documentation" → navigates to /docs
- Verify ActionSection is visible and functional
- Click "Run Evaluation" → simulation runs
- Observe complete flow: code → terminal → metrics
- Verify results are deterministic (run multiple times)

**Files/Areas:**
- `src/pages/Home.tsx`
- All component files created

**Acceptance Criteria:**
- [~] Home page loads correctly
- [~] Hero section is prominent and clear
- [~] CTAs navigate/scroll correctly
- [~] ActionSection is fully functional
- [~] Simulation is deterministic
- [ ] Professional appearance
- [ ] No console errors

**Validation:** Load home page; test entire user journey.

---

### TASK-055 — Create Responsive Hero & Landing Page Adjustments

**Priority:** P1  
**Requirements:** FR-079, FR-080, FR-082  
**Dependencies:** TASK-053  
**Objective:** Fine-tune responsive design for landing page on all devices.

**Implementation:**
- Test home page on:
  - Desktop (1920px, 1440px)
  - Tablet (768px, 1024px)
  - Mobile (375px, 414px)
- Adjust:
  - Hero section margins and padding
  - Button sizes and spacing
  - Font sizes
  - Pipeline visualization sizing
  - ActionSection layout
  - Spacing between sections
- Verify:
  - No horizontal overflow
  - Touch targets are adequate (48px+ on mobile)
  - Text is readable at all sizes

**Files/Areas:**
- `src/pages/Home.tsx`
- Component files (HeroSection, PipelineVisualization, etc.)

**Acceptance Criteria:**
- [~] Looks good on all screen sizes
- [~] No horizontal overflow
- [~] Touch targets are adequate
- [~] Text is readable
- [~] Professional appearance at all sizes

**Validation:** Test on actual devices or responsive emulator.

---

## PHASE 5: Source Anchors Visualization

### TASK-060 — Create SourceAnchorCard Component

**Priority:** P1  
**Requirements:** FR-023  
**Dependencies:** TASK-012, TASK-002  
**Objective:** Build source anchor metadata card.

**Implementation:**
- Create `src/components/features/SourceAnchorCard.tsx`
- Display fields:
  - Document: "cloudsync-guide.md"
  - Start: "1248"
  - End: "1327"
  - Status: "VALID" (with status indicator color)
  - Hash: "verified"
- Features:
  - Professional card styling
  - Subtle border and shadow
  - Clean layout
  - Responsive design
- Props: `document`, `start`, `end`, `status`, `hash`

**Files/Areas:**
- `src/components/features/SourceAnchorCard.tsx`

**Acceptance Criteria:**
- [~] All fields display
- [~] Status indicator shows color
- [ ] Professional appearance
- [ ] Responsive design
- [ ] TypeScript passes

**Validation:** Render card with demo data; verify styling.

---

### TASK-061 — Create SourceAnchorDemo Component

**Priority:** P1  
**Requirements:** FR-020, FR-021, FR-022, FR-023, FR-024  
**Dependencies:** TASK-060, TASK-002, TASK-052  
**Objective:** Build "Why source anchors?" section with document and anchor example.

**Implementation:**
- Create `src/components/features/SourceAnchorDemo.tsx`
- Content:
  - Heading: "Why source anchors?"
  - Sample document text: CloudSync deployment documentation excerpt
  - Highlighted span example: "CloudSync retries failed uploads three times before marking the operation as failed."
  - SourceAnchorCard component displaying anchor metadata
  - Explanation text: "SPANCHOR evaluates evidence against stable source locations..."
- Features:
  - Clear highlighting (subtle background color, e.g., light yellow or blue)
  - Professional layout
  - Responsive design
  - Proper typography hierarchy

**Files/Areas:**
- `src/components/features/SourceAnchorDemo.tsx`

**Acceptance Criteria:**
- [~] All elements display
- [~] Text is highlighted clearly
- [~] Anchor card is visible
- [~] Explanation is readable
- [ ] Responsive design
- [ ] Professional appearance
- [ ] TypeScript passes

**Validation:** Render section; verify highlighting and layout.

---

### TASK-062 — Create SourceAnchorSection (placeholder)

**Priority:** P1  
**Requirements:** FR-020 through FR-024  
**Dependencies:** TASK-061  
**Objective:** Integrate SourceAnchorDemo into home page as a full section.

**Implementation:**
- Create or integrate `src/components/features/SourceAnchorSection.tsx`
- Or update Home page to include SourceAnchorDemo
- Position in the home page flow (after ActionSection)
- Professional spacing and layout

**Files/Areas:**
- `src/pages/Home.tsx` or new component
- Component files

**Acceptance Criteria:**
- [~] Section displays on home page
- [ ] Professional spacing
- [ ] Responsive design
- [~] All content visible

**Validation:** Render home page; verify section is present and styled.

---

### TASK-063 — Create ComparisonPanel Component

**Priority:** P0  
**Requirements:** FR-025, FR-026, FR-027, FR-028, FR-029  
**Dependencies:** TASK-041, TASK-012, TASK-002  
**Objective:** Build animated baseline vs candidate comparison panel.

**Implementation:**
- Create `src/components/features/ComparisonPanel.tsx`
- Heading: "Detect retrieval regressions"
- Two-column layout:
  - BASELINE column:
    - Recall@5: 0.405
    - Precision@5: 0.020
    - Hit@5: 0.410
  - CANDIDATE column:
    - Recall@5: 0.249
    - Precision@5: 0.017
    - Hit@5: 0.260
- Summary below:
  - Improved: 6
  - Unchanged: 75
  - Regressed: 19
- Features:
  - Metrics animate into view
  - Counts animate into view
  - Neutral language (no "better" or "worse" implied)
  - Responsive layout (stacked on mobile)
  - Professional styling

**Files/Areas:**
- `src/components/features/ComparisonPanel.tsx`

**Acceptance Criteria:**
- [~] Both columns display correctly
- [~] Metrics are accurate
- [~] Summary shows correct counts
- [ ] Animation is smooth
- [~] Language is neutral
- [ ] Responsive design
- [ ] Professional appearance
- [ ] TypeScript passes

**Validation:** Render component; verify all values and animation.

---

## PHASE 6: Baseline/Candidate Comparison

### TASK-064 — Integrate ComparisonPanel into Home Page

**Priority:** P0  
**Requirements:** FR-025 through FR-029  
**Dependencies:** TASK-063  
**Objective:** Add ComparisonPanel to home page as a dedicated section.

**Implementation:**
- Update `src/pages/Home.tsx`
- Add ComparisonPanel section after ActionSection
- Professional spacing and layout
- Responsive on all devices

**Files/Areas:**
- `src/pages/Home.tsx`

**Acceptance Criteria:**
- [ ] Section displays on home page
- [ ] Professional spacing
- [ ] Responsive design
- [~] All metrics visible
- [~] Animation works

**Validation:** Render home page; verify section is present and styled.

---

### TASK-065 — Create RegressionTable Component

**Priority:** P1  
**Requirements:** FR-030, FR-031, FR-032, FR-033  
**Dependencies:** TASK-012, TASK-002, TASK-031  
**Objective:** Build interactive regression query results table.

**Implementation:**
- Create `src/components/features/RegressionTable.tsx`
- Columns: Query, Baseline, Candidate, Delta, Status
- Features:
  - Sortable columns
  - Filterable by status (All, Improved, Unchanged, Regressed)
  - Searchable by query ID
  - Responsive table layout
  - Professional styling
- Props: `data`, `onFilter`, `onSort`, `onSearch`

**Files/Areas:**
- `src/components/features/RegressionTable.tsx`

**Acceptance Criteria:**
- [~] Table displays data correctly
- [~] Sorting works
- [~] Filtering works
- [~] Search works
- [ ] Responsive design
- [ ] Professional appearance
- [ ] TypeScript passes

**Validation:** Render table with demo data; test all features.

---

### TASK-066 — Create RegressionSection (placeholder)

**Priority:** P1  
**Requirements:** FR-030 through FR-033  
**Dependencies:** TASK-065  
**Objective:** Add RegressionTable to home page or dedicated page.

**Implementation:**
- Create or integrate regression results section
- Include RegressionTable component
- Professional layout and context

**Files/Areas:**
- Component files

**Acceptance Criteria:**
- [~] Section displays
- [~] Table is functional
- [ ] Professional appearance
- [ ] TypeScript passes

**Validation:** Render section; test table interactivity.

---

## PHASE 7: Documentation System

### TASK-070 — Create DocsSidebar Component

**Priority:** P0  
**Requirements:** FR-042, FR-043, FR-044  
**Dependencies:** TASK-002, TASK-015  
**Objective:** Build sidebar navigation for documentation pages.

**Implementation:**
- Create `src/components/layouts/DocsSidebar.tsx`
- Sections:
  - Introduction
  - Getting Started (Installation, Quickstart)
  - Core Concepts (Concepts, Anchors, Gold Sets)
  - Evaluation (Metrics, Comparison)
  - Adapters
  - CLI
  - Examples
  - Reference (Limitations)
- Features:
  - Hierarchical navigation
  - Current page highlighted
  - Collapsible sections
  - Mobile drawer (hamburger menu)
  - Active link highlighting
  - Smooth transitions

**Files/Areas:**
- `src/components/layouts/DocsSidebar.tsx`

**Acceptance Criteria:**
- [~] All sections present
- [~] Current page highlighted
- [~] Links navigate correctly
- [~] Mobile menu works
- [~] Professional styling
- [ ] TypeScript passes

**Validation:** Render sidebar; test navigation and active state.

---

### TASK-071 — Create DocsLayout Component

**Priority:** P0  
**Requirements:** FR-043  
**Dependencies:** TASK-070, TASK-017, TASK-018  
**Objective:** Build three-column documentation layout.

**Implementation:**
- Create `src/components/layouts/DocsLayout.tsx`
- Layout:
  - Navbar (top)
  - Left: DocsSidebar
  - Center: Main content area (children)
  - Right: "On this page" table of contents
  - Footer (bottom)
- Features:
  - Responsive (sidebar collapses on mobile)
  - Right column collapses on mobile
  - Professional spacing
  - Clean, GitHub/Vercel-style design

**Files/Areas:**
- `src/components/layouts/DocsLayout.tsx`

**Acceptance Criteria:**
- [~] Layout renders correctly
- [~] All three columns present on desktop
- [~] Responsive on mobile
- [ ] Professional appearance
- [ ] TypeScript passes

**Validation:** Render layout on desktop and mobile; verify responsiveness.

---

### TASK-072 — Create DocumentationPage Component

**Priority:** P0  
**Requirements:** FR-042 through FR-056  
**Dependencies:** TASK-071, TASK-019  
**Objective:** Create template component for individual documentation pages.

**Implementation:**
- Create `src/components/docs/DocumentationPage.tsx`
- Props: `title`, `description`, `children`, `route`
- Features:
  - Wraps content with DocsLayout
  - Renders markdown or JSX content
  - Proper typography hierarchy
  - "On this page" auto-generates from H2/H3 headings
  - Metadata for SEO

**Files/Areas:**
- `src/components/docs/DocumentationPage.tsx`

**Acceptance Criteria:**
- [~] Component renders correctly
- [~] Table of contents generates
- [~] Proper typography
- [ ] TypeScript passes

**Validation:** Create test page using component.

---

### TASK-073 — Create Documentation Pages & Routes

**Priority:** P0  
**Requirements:** FR-042 through FR-056  
**Dependencies:** TASK-072, TASK-032  
**Objective:** Create all documentation page routes with content from docsContent data.

**Implementation:**
- Create page components in `src/pages/docs/`:
  - `Index.tsx` (Introduction)
  - `Installation.tsx` (/docs/installation)
  - `Quickstart.tsx` (/docs/quickstart)
  - `Concepts.tsx` (/docs/concepts)
  - `Anchors.tsx` (/docs/anchors)
  - `GoldSets.tsx` (/docs/gold-sets)
  - `Metrics.tsx` (/docs/metrics)
  - `Comparison.tsx` (/docs/comparison)
  - `Adapters.tsx` (/docs/adapters)
  - `CLI.tsx` (/docs/cli)
  - `Testing.tsx` (/docs/testing)
  - `Limitations.tsx` (/docs/limitations)
- Each page:
  - Uses DocumentationPage component
  - Imports content from docsContent data
  - Renders properly formatted content
  - Has correct route

**Files/Areas:**
- `src/pages/docs/` (all files)
- `src/App.tsx` (route configuration)

**Acceptance Criteria:**
- [~] All routes accessible
- [~] Content displays correctly
- [~] Navigation works
- [ ] Professional appearance
- [ ] TypeScript passes

**Validation:** Navigate to each doc page; verify content.

---

## PHASE 8: Playground

### TASK-080 — Create PlaygroundPage Component

**Priority:** P0  
**Requirements:** FR-036, FR-037, FR-038, FR-039, FR-040, FR-041  
**Dependencies:** TASK-016, TASK-043, TASK-044, TASK-035, TASK-041, TASK-002  
**Objective:** Build interactive playground page with demo controls.

**Implementation:**
- Create `src/pages/Playground.tsx`
- Structure:
  - Heading: "SPANCHOR Playground"
  - Subheading: "Explore retrieval evaluation without setting up a backend."
  - Dataset selector (CloudSync baseline/candidate)
  - Code editor (CodeBlock)
  - Run button
  - Execution visualization (ExecutionOutput)
  - Metrics display
  - Simulation phase checklist
- Features:
  - Same simulation engine as home page
  - Deterministic results
  - Responsive layout (stacked on mobile)
  - Professional styling
  - Clear labeling that this is a frontend simulation

**Files/Areas:**
- `src/pages/Playground.tsx`
- Component files

**Acceptance Criteria:**
- [~] Page renders correctly
- [~] All controls work
- [~] Simulation runs
- [~] Results display correctly
- [ ] Responsive design
- [ ] Professional appearance
- [ ] TypeScript passes

**Validation:** Load playground; run simulation; verify results.

---

## PHASE 9: Examples

### TASK-090 — Create ExamplesPage Component

**Priority:** P1  
**Requirements:** FR-057, FR-058, FR-059  
**Dependencies:** TASK-016, TASK-033, TASK-002  
**Objective:** Create examples showcase page with 6 code examples.

**Implementation:**
- Create `src/pages/Examples.tsx`
- Display all 6 examples from examplesData:
  1. Basic Evaluation
  2. Baseline vs Candidate
  3. Source Anchors
  4. LangChain Adapter
  5. LlamaIndex Adapter
  6. Gold Set Import
- Each example displays:
  - Title and description
  - Code block (syntax highlighted)
  - Expected output
  - Visual preview (if applicable)
- Features:
  - Responsive grid layout
  - Professional styling
  - Copy code functionality
  - Clear explanations

**Files/Areas:**
- `src/pages/Examples.tsx`

**Acceptance Criteria:**
- [~] All 6 examples display
- [~] Code is syntax highlighted
- [ ] Descriptions are clear
- [ ] Responsive layout
- [ ] Professional appearance
- [ ] TypeScript passes

**Validation:** Load examples page; verify all 6 are displayed correctly.

---

## PHASE 10: API Documentation

### TASK-100 — Create APIPage Component

**Priority:** P1  
**Requirements:** FR-060, FR-061, FR-062  
**Dependencies:** TASK-016, TASK-034, TASK-002  
**Objective:** Create API documentation page with expandable items.

**Implementation:**
- Create `src/pages/API.tsx`
- Display all major items from apiDocsData:
  - Document (class/interface)
  - Anchor (class/interface)
  - Span (class/interface)
  - RetrievalResult (class/interface)
  - EvaluationResult (class/interface)
  - evaluate() (function)
  - compare() (function)
- Each item has:
  - Expandable/collapsible section
  - Signature (for functions)
  - Parameters documented
  - Return value documented
  - Example code
  - Description
- Features:
  - Responsive layout
  - Professional styling
  - Copy code functionality
  - Clear organization

**Files/Areas:**
- `src/pages/API.tsx`

**Acceptance Criteria:**
- [~] All items display
- [~] Expandable/collapsible works
- [~] Information is accurate
- [~] Code examples present
- [ ] Responsive layout
- [ ] Professional appearance
- [ ] TypeScript passes

**Validation:** Load API page; expand items; verify content.

---

## PHASE 11: Architecture Page

### TASK-110 — Create ArchitecturePage Component

**Priority:** P1  
**Requirements:** FR-063, FR-064, FR-065  
**Dependencies:** TASK-002, TASK-005  
**Objective:** Create architecture visualization page with interactive diagram.

**Implementation:**
- Create `src/pages/Architecture.tsx`
- Display interactive pipeline diagram:
  ```
  Source Documents
  ↓
  Canonicalization
  ↓
  Chunking
  ↓
  Retrieval
  ↓
  Retrieved Results
  ↓
  SPANCHOR (with sub-nodes: Anchors, Metrics, Comparison, Regression)
  ↓
  CI / Test Results
  ```
- Features:
  - Visual nodes and connections
  - Clickable nodes (open explanation modal or inline)
  - Smooth animations
  - Responsive layout
  - Professional styling
  - Respects prefers-reduced-motion

**Files/Areas:**
- `src/pages/Architecture.tsx`

**Acceptance Criteria:**
- [~] Diagram displays correctly
- [~] Nodes are interactive
- [~] Explanations display
- [ ] Responsive layout
- [ ] Animations are smooth
- [ ] Professional appearance
- [ ] TypeScript passes

**Validation:** Load architecture page; click nodes; verify explanations.

---

## PHASE 12: Responsive Design & Testing

### TASK-120 — Test Responsive Design (All Pages)

**Priority:** P0  
**Requirements:** FR-079, FR-080  
**Dependencies:** All previous phases  
**Objective:** Comprehensive testing of responsive design across all pages.

**Implementation:**
- Test on all screen sizes:
  - Desktop: 1920px, 1440px, 1024px
  - Tablet: 768px, 810px
  - Mobile: 375px, 414px
- Verify on each page:
  - No horizontal overflow
  - Touch targets are 48px+
  - Text is readable
  - Images scale properly
  - Navigation is accessible
  - Layouts stack/reflow correctly
- Fix any layout issues

**Files/Areas:**
- All component and page files

**Acceptance Criteria:**
- [~] All pages render correctly on all sizes
- [ ] No horizontal overflow
- [~] Touch targets adequate
- [ ] Professional appearance at all sizes
- [~] Navigation accessible on mobile

**Validation:** Test on actual devices or responsive emulator.

---

### TASK-121 — Test Accessibility

**Priority:** P0  
**Requirements:** FR-081, FR-085 through FR-090  
**Dependencies:** All previous phases  
**Objective:** Comprehensive accessibility testing.

**Implementation:**
- Check all pages for:
  - Semantic HTML (proper heading hierarchy, sections, etc.)
  - Keyboard navigation (Tab, Enter, ESC, Arrow keys)
  - Focus states (visible focus indicators)
  - ARIA labels on buttons, links, modals
  - Color contrast (WCAG AA minimum)
  - Reduced motion support (prefers-reduced-motion respected)
  - Alt text on images (if any decorative, mark as such)
  - Form labels (if any forms exist)
  - Error messages are clear
  - Loading states are announced
- Fix any accessibility issues

**Files/Areas:**
- All component and page files

**Acceptance Criteria:**
- [~] Keyboard navigation works throughout
- [~] Focus states are visible
- [~] Color contrast is adequate
- [~] ARIA labels present where needed
- [~] Reduced motion respected
- [~] Semantic HTML used

**Validation:** Test with keyboard; use accessibility checker; test with screen reader simulator.

---

### TASK-122 — Test Reduced Motion Support

**Priority:** P1  
**Requirements:** FR-081  
**Dependencies:** All previous phases  
**Objective:** Verify all animations respect prefers-reduced-motion preference.

**Implementation:**
- In system settings (or browser dev tools), enable `prefers-reduced-motion`
- Test all pages and verify:
  - Animations are instant or very fast
  - No multi-step animations
  - Content still displays and functions
  - User experience is not degraded
- Fix any issues

**Files/Areas:**
- All animation files and components

**Acceptance Criteria:**
- [~] All animations respect prefers-reduced-motion
- [~] Content displays instantly
- [~] Functionality not impaired
- [~] User experience is still good

**Validation:** Enable prefers-reduced-motion in browser; test all pages.

---

## PHASE 13: Quality Assurance

### TASK-130 — Final TypeScript & Lint Verification

**Priority:** P0  
**Requirements:** FR-102, NFR-001  
**Dependencies:** All previous phases  
**Objective:** Verify TypeScript strict mode and linting.

**Implementation:**
- Run `npm run build`
- Run `npx tsc --noEmit` to check TypeScript
- Run linter (ESLint)
- Fix any errors or warnings
- Ensure:
  - No `any` types
  - No console errors/warnings (except deliberate logging)
  - All imports resolved
  - No unused variables/imports
  - Code style is consistent

**Files/Areas:**
- All source files

**Acceptance Criteria:**
- [ ] TypeScript passes strict mode
- [~] Linter has no errors
- [~] Build succeeds
- [ ] No console errors
- [~] Code is clean

**Validation:** Run `npm run build` and linter; check output.

---

### TASK-131 — Test All Routes & Navigation

**Priority:** P0  
**Requirements:** FR-042, FR-066 through FR-077  
**Dependencies:** All previous phases  
**Objective:** Verify all routes are accessible and navigation works.

**Implementation:**
- Test each route:
  - `/` (Home)
  - `/playground` (Playground)
  - `/examples` (Examples)
  - `/api` (API docs)
  - `/architecture` (Architecture)
  - `/docs` (Docs root)
  - `/docs/installation`, `/docs/quickstart`, etc. (all doc pages)
  - `/notfound` or invalid route (404 page)
- Verify:
  - Each route loads
  - Content displays correctly
  - URL updates in address bar
  - Browser back/forward works
  - Navbar links work
  - Footer links work
  - All external links open in new tab

**Files/Areas:**
- `src/App.tsx`
- All page files

**Acceptance Criteria:**
- [ ] All routes accessible
- [ ] Navigation works
- [~] URL updates correctly
- [~] Back/forward work
- [~] External links work

**Validation:** Test each route in browser; verify navigation.

---

### TASK-132 — Test Deterministic Simulation

**Priority:** P0  
**Requirements:** FR-014, FR-016  
**Dependencies:** TASK-035, TASK-031  
**Objective:** Verify simulation is deterministic.

**Implementation:**
- Run simulation on home page and playground multiple times
- Verify:
  - Same steps execute in same order
  - Same metrics displayed each time
  - Same query results shown
  - Same timing between steps
  - Terminal output is identical
  - Results are 100% reproducible
- Document findings

**Files/Areas:**
- `src/hooks/useSimulation.ts`
- `src/data/demoData.ts`

**Acceptance Criteria:**
- [~] Simulation produces identical results on every run
- [~] No randomness in data or timing
- [~] Metrics match spec exactly
- [~] All results are reproducible

**Validation:** Run simulation 10+ times; verify identical results.

---

### TASK-133 — Test External Links

**Priority:** P0  
**Requirements:** FR-098, FR-099, FR-100  
**Dependencies:** All previous phases  
**Objective:** Verify all external links are correct and functional.

**Implementation:**
- Test all external links:
  - GitHub: https://github.com/Mukeshram-07/spanchor
  - PyPI: https://pypi.org/project/spanchor/
- Verify:
  - Links open in new tab (target="_blank")
  - URLs are correct
  - Links are not broken

**Files/Areas:**
- All component files

**Acceptance Criteria:**
- [~] All external links work
- [~] Links open in new tab
- [~] URLs are correct

**Validation:** Click all external links; verify they work.

---

## PHASE 14: Final Polish & Documentation

### TASK-140 — Final UI/UX Review

**Priority:** P0  
**Requirements:** Design System, All visual requirements  
**Dependencies:** All previous phases  
**Objective:** Comprehensive UI/UX review and final polish.

**Implementation:**
- Review entire website:
  - Spacing consistency (margins, padding, gaps)
  - Typography hierarchy and consistency
  - Visual hierarchy (importance conveyed through size, color, position)
  - Alignment (no misaligned elements)
  - Color consistency (using design tokens)
  - Button states (hover, focus, disabled, loading)
  - Animations (smooth, professional, purposeful)
  - Mobile layout quality
  - Loading states
  - Completion states
  - Error states
- Make final adjustments for polish

**Files/Areas:**
- All component and page files

**Acceptance Criteria:**
- [~] Consistent spacing throughout
- [~] Proper typography hierarchy
- [~] Visual hierarchy is clear
- [~] All elements aligned
- [~] Professional color palette
- [~] Button states all work
- [ ] Animations are smooth
- [~] Polish is evident

**Validation:** Full visual walkthrough of website.

---

### TASK-141 — SEO & Meta Tags

**Priority:** P1  
**Requirements:** FR-091, FR-092, FR-093, FR-094  
**Dependencies:** All pages  
**Objective:** Add SEO metadata to all pages.

**Implementation:**
- Update `src/main.tsx` or create `src/utils/seo.ts`
- Add to each page:
  - `<title>` (unique per page)
  - `<meta name="description">`
  - `<meta property="og:title">`
  - `<meta property="og:description">`
  - `<meta property="og:image">` (if applicable)
- Homepage:
  - Title: "SPANCHOR — RAG Retrieval Regression Testing"
  - Description: "Source-anchored regression testing for RAG retrieval pipelines. Deterministic, local-first, frontend-only."
- Other pages:
  - Relevant titles and descriptions

**Files/Areas:**
- `index.html`
- `src/main.tsx` or SEO utility

**Acceptance Criteria:**
- [~] All pages have proper titles
- [~] Descriptions are present
- [~] Open Graph tags present
- [~] SEO compliant
- [~] Professional

**Validation:** Check HTML head; verify all tags present.

---

### TASK-142 — Final Build & Production Verification

**Priority:** P0  
**Requirements:** FR-102, NFR-001  
**Dependencies:** All previous phases  
**Objective:** Final build and production readiness verification.

**Implementation:**
- Run `npm run build`
- Verify:
  - Build completes without errors
  - No warnings (or explain why acceptable)
  - `dist/` folder is created
  - All assets are bundled
  - Build size is reasonable
  - No console errors in built version
  - All routes work in production build
  - Assets are properly cached/versioned

**Files/Areas:**
- `vite.config.ts`
- All source files
- `dist/` folder

**Acceptance Criteria:**
- [~] Production build succeeds
- [~] No errors or warnings
- [~] Build size is reasonable
- [~] All routes work
- [~] Assets load correctly

**Validation:** Run `npm run build`; verify `dist/` folder; test all routes.

---

## FINAL VALIDATION TASK

### TASK-FINAL — Production Validation Checklist

**Priority:** P0  
**Requirements:** All FR and NFR requirements  
**Dependencies:** All previous tasks  
**Objective:** Final comprehensive validation that all requirements are met.

**Implementation:**
- Complete validation checklist:

**Acceptance Criteria:**
- [~] All P0 requirements implemented (47 requirements)
- [~] All P1 requirements reviewed (30 requirements)
- [~] P2 requirements addressed (8 requirements)
- [~] TypeScript strict mode: PASS
- [~] ESLint: PASS
- [~] Production build: PASS
- [~] All routes work (/, /playground, /examples, /api, /architecture, /docs/*, 404)
- [~] Playground works end-to-end
- [~] Simulation is deterministic (100% reproducible)
- [~] CODE → RUN → VISUALIZATION centerpiece works perfectly
- [~] Home page is engaging and clear
- [~] Navigation works throughout
- [ ] Responsive on all devices
- [~] Accessibility: keyboard navigation, focus states, ARIA labels, contrast
- [ ] Reduced motion respected
- [~] GitHub link works: https://github.com/Mukeshram-07/spanchor
- [~] PyPI link works: https://pypi.org/project/spanchor/
- [~] No backend exists (frontend-only ✓)
- [~] No arbitrary code execution (deterministic demo ✓)
- [~] No unsupported product claims (doc pages are accurate ✓)
- [ ] No console errors or warnings
- [~] SEO metadata present
- [~] Professional appearance and polish

**Validation:** Complete all checks; document results.

---

## 4. Dependency Graph

```
TASK-001 (Setup)
    ↓
TASK-002 (Tailwind)
    ↓
TASK-003 (Dependencies)
    ↓
TASK-004 (Routing)
    ├─→ TASK-005 (Animations)
    │
    └─→ TASK-010-020 (Design System & UI Components)
            ├─→ TASK-030-037 (Demo Data & Simulation)
            │   ├─→ TASK-040-047 (Execution Visualization)
            │   │   ├─→ TASK-050-055 (Landing Page)
            │   │   ├─→ TASK-080 (Playground)
            │   │   └─→ TASK-090 (Examples)
            │   │
            │   └─→ TASK-060-066 (Source Anchors & Comparison)
            │
            └─→ TASK-070-073 (Documentation System)
                └─→ TASK-100 (API Docs)
                └─→ TASK-110 (Architecture)

TASK-120-133 (Testing & QA)
    └─→ TASK-140-142 (Final Polish)
        └─→ TASK-FINAL (Production Validation)
```

---

## 5. Requirement Traceability Matrix

| Task | Requirements | Phase | Priority | Status |
|------|--------------|-------|----------|--------|
| TASK-001 | FR-102, NFR-001 | 0 | P0 | Ready |
| TASK-002 | FR-102 | 0 | P0 | Ready |
| TASK-003 | FR-102 | 0 | P0 | Ready |
| TASK-004 | FR-042, FR-066 | 0 | P0 | Ready |
| TASK-005 | FR-082, FR-083, FR-084 | 0 | P1 | Ready |
| TASK-010 | FR-004, FR-005, FR-066 | 1 | P0 | Ready |
| TASK-011 | FR-003 | 1 | P0 | Ready |
| TASK-012 | FR-023 | 1 | P0 | Ready |
| TASK-013 | FR-010 | 1 | P0 | Ready |
| TASK-014 | Design System | 1 | P1 | Ready |
| TASK-015 | FR-066 (mobile) | 1 | P0 | Ready |
| TASK-016 | FR-007, FR-059 | 1 | P0 | Ready |
| TASK-017 | FR-066-070 | 1 | P0 | Ready |
| TASK-018 | FR-098, FR-099 | 1 | P0 | Ready |
| TASK-019 | Design System | 1 | P1 | Ready |
| TASK-020 | Design System | 1 | P1 | Ready |
| TASK-030 | FR-104-106, FR-015-016 | 2 | P0 | Ready |
| TASK-031 | FR-104-106, FR-016 | 2 | P0 | Ready |
| TASK-032 | FR-045-056 | 2 | P1 | Ready |
| TASK-033 | FR-058-059 | 2 | P1 | Ready |
| TASK-034 | FR-060-062 | 2 | P1 | Ready |
| TASK-035 | FR-015-016, FR-014 | 2 | P0 | Ready |
| TASK-036 | FR-012, FR-084 | 2 | P0 | Ready |
| TASK-037 | FR-019, FR-083 | 2 | P1 | Ready |
| TASK-040 | FR-018-019, FR-031 | 3 | P0 | Ready |
| TASK-041 | FR-012, FR-084 | 3 | P0 | Ready |
| TASK-042 | FR-010 | 3 | P0 | Ready |
| TASK-043 | FR-009-010, FR-013 | 3 | P0 | Ready |
| TASK-044 | FR-008, FR-014 | 3 | P0 | Ready |
| TASK-045 | FR-007-014 | 3 | P0 | Ready |
| TASK-046 | FR-015-016 | 3 | P1 | Ready |
| TASK-047 | FR-014, FR-016 | 3 | P1 | Ready |
| TASK-050 | FR-001-006 | 4 | P0 | Ready |
| TASK-051 | FR-006, FR-082 | 4 | P0 | Ready |
| TASK-052 | FR-020, FR-025 | 4 | P1 | Ready |
| TASK-053 | FR-001-006 | 4 | P0 | Ready |
| TASK-054 | FR-001-014 | 4 | P0 | Ready |
| TASK-055 | FR-079-082 | 4 | P1 | Ready |
| TASK-060 | FR-023 | 5 | P1 | Ready |
| TASK-061 | FR-020-024 | 5 | P1 | Ready |
| TASK-062 | FR-020-024 | 5 | P1 | Ready |
| TASK-063 | FR-025-029 | 6 | P0 | Ready |
| TASK-064 | FR-025-029 | 6 | P0 | Ready |
| TASK-065 | FR-030-033 | 6 | P1 | Ready |
| TASK-066 | FR-030-033 | 6 | P1 | Ready |
| TASK-070 | FR-042-044 | 7 | P0 | Ready |
| TASK-071 | FR-043 | 7 | P0 | Ready |
| TASK-072 | FR-042-056 | 7 | P0 | Ready |
| TASK-073 | FR-042-056 | 7 | P0 | Ready |
| TASK-080 | FR-036-041 | 8 | P0 | Ready |
| TASK-090 | FR-057-059 | 9 | P1 | Ready |
| TASK-100 | FR-060-062 | 10 | P1 | Ready |
| TASK-110 | FR-063-065 | 11 | P1 | Ready |
| TASK-120 | FR-079-080 | 12 | P0 | Ready |
| TASK-121 | FR-081, FR-085-090 | 12 | P0 | Ready |
| TASK-122 | FR-081 | 12 | P1 | Ready |
| TASK-130 | FR-102, NFR-001 | 13 | P0 | Ready |
| TASK-131 | FR-042, FR-066-077 | 13 | P0 | Ready |
| TASK-132 | FR-014, FR-016 | 13 | P0 | Ready |
| TASK-133 | FR-098-100 | 13 | P0 | Ready |
| TASK-140 | All visual | 14 | P0 | Ready |
| TASK-141 | FR-091-094 | 14 | P1 | Ready |
| TASK-142 | FR-102, NFR-001 | 14 | P0 | Ready |
| TASK-FINAL | All | 15 | P0 | Ready |

---

## 6. Summary

- **Total Tasks**: 85
- **P0 Tasks**: 47 (core implementation)
- **P1 Tasks**: 30 (important features)
- **P2 Tasks**: 8 (polish/optional)
- **Estimated Duration**: 200-250 developer-hours (depending on experience)
- **Phase 0-3**: Foundation (80 hours)
- **Phase 4-6**: Core Experience (60 hours)
- **Phase 7-11**: Documentation & Examples (50 hours)
- **Phase 12-14**: Polish & QA (30 hours)

---

## 7. Important Notes

1. **Frontend-Only**: No backend. All data is deterministic and local.
2. **Deterministic Simulation**: All demo runs produce identical results.
3. **No Backend Claims**: Documentation is accurate to actual SPANCHOR library.
4. **Accessibility**: Full keyboard navigation, ARIA labels, reduced motion support.
5. **Responsive**: Works on all device sizes without horizontal overflow.
6. **Professional Quality**: Production-ready code, clean TypeScript, no technical debt.

---

**This task plan is ready for execution. Begin with Phase 0 (Project Foundation) and proceed sequentially.**
