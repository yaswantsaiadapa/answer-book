# Production Architecture & Layout Guide

> **Purpose:** This document establishes the engineering guidelines, directory layout, architectural principles, and phased migration roadmap for adapting the **Paper to Solution Book** repository into a production-grade AI service.

---

## 1. Project Context & Stack

* **Service:** Standalone FastAPI service taking an uploaded question paper (PDF/photo) and generating a full solution book with step-by-step answers, mark breakdowns, misconception analysis, and honest confidence scores.
* **Stack:** Python 3.11+ · FastAPI · LangGraph · SymPy · PyMuPDF / Vision models · SSE (Server-Sent Events) streaming.
* **Roles in Team:**
  * **Role 1 (Ingestion & Structure):** PDF/OCR extraction $\rightarrow$ `Paper` object.
  * **Role 2 (Solve & Verify — Our Scope):** LangGraph multi-agent core (`Paper` $\rightarrow$ `SolvedPaper`).
  * **Role 3 (Assembly & Serving):** FastAPI endpoints, SSE streaming, PDF rendering, fingerprint cache.

---

## 2. Target Production Structure

```text
├── app/
│   ├── api/            # FastAPI routes, dependencies, request/response schemas (frozen contract)
│   ├── core/           # Configuration (Pydantic Settings), logging, tracing, custom exceptions
│   ├── ingest/         # Source parsing, PDF text extraction, OCR interfaces (Role 1 handoff)
│   ├── retrieve/       # Syllabus/rubric retrieval and knowledge base lookup
│   ├── generate/       # LangGraph workflows, state definitions, planner, solvers, verifiers
│   │   ├── state.py    # LangGraph State schemas (PaperState, QuestionState)
│   │   ├── graph.py    # StateGraph definition, node registration, conditional edges
│   │   ├── nodes/      # planner, math_solver, mcq_solver, theory_solver, normalizer
│   │   └── verifiers/  # sympy_verifier, constraint_verifier, rubric_verifier
│   ├── llm/            # Provider-agnostic LLM interface (OpenAI, Anthropic, Gemini, local mock)
│   ├── store/          # Fingerprint cache, paper metadata store, solution persistence
│   ├── jobs/           # Background workers for asynchronous batch paper processing
│   ├── defects/        # Answer validation, confidence calibration, schema verification
│   └── main.py         # Application entrypoint and lifecycle management
├── tests/
│   ├── unit/           # Isolated deterministic unit tests (mocked LLMs, SymPy unit tests)
│   └── contract/       # Frozen API contract tests (/papers, /papers/{id}/solutions, SSE)
├── eval/
│   ├── golden/         # Set A (12 papers with known answer keys) version-controlled
│   ├── metrics/        # Correctness, Honest Confidence, Structure Recovery, Cost/Latency
│   ├── runs/           # Historical evaluation runs and benchmark reports
│   └── run.py          # CLI evaluation runner script
├── docs/
│   ├── ARCHITECTURE.md # LangGraph design, state contracts, routing logic
│   ├── OPERATIONS.md   # Deployment, environment config, scaling, cache warming
│   ├── EVALUATION.md   # Benchmark scoring methodology (Set A vs Set B rubric)
│   ├── GLOSSARY.md     # Project terminology (Symbolic verification, Mark Split, etc.)
│   └── WEAKNESSES.md   # Known failure modes (blurry photos, handwriting, complex diagrams)
├── seed/               # Local sample papers (question_paper_455.pdf, 463.pdf, static_test_papers.json)
├── learn/              # Onboarding notes, architectural decision records (ADRs), traces
├── docker-compose.yml  # Local dev stack (FastAPI + Redis/Cache)
├── Dockerfile          # Container build definition
├── Makefile            # Standard developer commands (test, lint, run, eval)
├── .env.example        # Centralized environment variable template
└── pyproject.toml      # Poetry / pip dependencies and project metadata
```

---

## 3. Core Architecture Principles

1. **Clean Separation of Concerns:**
   Keep API routing (`app/api`), graph business logic (`app/generate`), persistence (`app/store`), and external integrations (`app/llm`) strictly decoupled.
2. **Provider-Agnostic LLM Layer:**
   All model invocations must go through an abstract interface (`app/llm/base.py`). This allows hot-swapping between Gemini, OpenAI, Claude, or deterministic mock models without changing graph nodes.
3. **Deterministic Testing:**
   Tests in `tests/` must NEVER call external paid APIs or depend on external networks. All LLM calls must be mockable with deterministic fixtures.
4. **Evaluation as a First-Class Citizen:**
   Maintain an `eval/` harness scored directly on the project rubric:
   * Correct answers (30 pts)
   * Honest confidence calibration (20 pts)
   * Speed and cost tracking (10 pts)
5. **Centralized Configuration:**
   All configurations loaded via `app/core/config.py` using `pydantic-settings` from `.env`.
6. **Thin Handlers & Background Execution:**
   `POST /papers` responds immediately with `202 Accepted` and `paper_id`. Solving runs as a background task while streaming progress via SSE.
7. **Documented Limitations & Operations:**
   Known failure modes (e.g., photo skew, OCR degradation) documented in `WEAKNESSES.md`.
8. **Developer Ergonomics via Makefile:**
   Common tasks exposed through simple commands: `make dev`, `make test`, `make eval`, `make lint`.
9. **Avoid Over-Engineering:**
   Only create components that serve the actual project requirements (LangGraph solving, SymPy verification, frozen API contract).
10. **Preserve Frozen Contracts:**
    Strict adherence to Section 3 of `Project_BRIEF_solution_book.md`. Never alter API payload schemas.

---

## 4. Current File Mapping to Target Layout

| Current File | Target Location | Rationale |
| :--- | :--- | :--- |
| `papers/question_paper_455.pdf` | `seed/papers/question_paper_455.pdf` | Sample input data belongs in `seed/` |
| `papers/question_paper_463.pdf` | `seed/papers/question_paper_463.pdf` | Sample input data belongs in `seed/` |
| `src/static_test_papers.json` | `seed/static_test_papers.json` | Golden fixture for prototype testing |
| `src/diagram.md` | `docs/ARCHITECTURE.md` | Core graph architecture documentation |
| `src/notes.md` | `docs/WEAKNESSES.md` & `learn/ADR_roadmap.md` | Deferred features, known gaps, roadmap |
| `Project_BRIEF_solution_book.md`| `docs/PROJECT_BRIEF.md` | Foundational specification document |

---

## 5. Phased Incremental Migration Plan

### Phase 1: Prototype Foundation (Current Focus)
* Implement standalone `PrototypeQuestionState` and `generate/` graph nodes (`planner`, `math_solver`, `mcq_solver`, `theory_solver`).
* Validate end-to-end execution against `seed/static_test_papers.json` with mocked/deterministic LLM responses.

### Phase 2: Layout & Infrastructure Scaffolding
* Set up `app/core/config.py`, `app/llm/` provider abstraction, and `.env.example`.
* Add `tests/unit/` for deterministic node testing and `tests/contract/` for API schema validation.

### Phase 3: Verification & Confidence Layer
* Add `generate/verifiers/sympy_verifier.py` for mathematical verification.
* Add `defects/confidence.py` for grounded confidence scoring.
* Implement the self-healing retry loop.

### Phase 4: API & Streaming Integration
* Wire `app/api/` endpoints according to the frozen contract.
* Implement SSE event dispatch (`event: solution`, `event: progress`, `event: done`).
* Set up `Makefile` and `Dockerfile`.
