# Engineering Notes: Deferred Features & Future Roadmap

This document captures all architectural components discussed for the full system that are intentionally **excluded** from the initial prototype to maintain high velocity and simplicity.

---

## 1. Diagram & Multimodal Solver
* **What was discussed:** A dedicated `diagram_solver` using Vision-Language Models (VLMs) to process visual image crops (e.g., circuits, geometric figures, ray optics).
* **Why deferred:** Image parsing and coordinate/label alignment add latency and complexity. For the prototype, we assume text-only prompts or handle diagram questions via generic description fallbacks.

---

## 2. Independent Verification Layer
In the prototype, solvers directly generate answers without secondary verification (`verified_by: "none"`). The following verifiers are saved for the next iteration:

1. **Symbolic Math Verifier (SymPy Sandbox):**
   * Translates math steps into deterministic Python/SymPy equations to catch calculation mistakes.
2. **MCQ Premise & Constraint Verifier:**
   * Validates that the selected option uniquely satisfies the question premise without contradictions.
3. **Diagram Consistency Verifier:**
   * Ensures numbers and labels extracted in the text match the visual image crop.
4. **Rubric & Syllabus Keyword Verifier:**
   * Cross-checks descriptive answers against syllabus marking guidelines to ensure all required keywords are present.

---

## 3. Self-Healing Feedback & Retry Loop
* **What was discussed:** When a verifier catches an error, it generates a "red-pen" critique hint (e.g., *"Step 2 arithmetic gave 18 instead of 4"*) and loops back to the solver with an incremented `retry_count` (max 2 retries).
* **Prototype behavior:** One-shot generation. The solver executes once and routes directly to the contract normalizer.

---

## 4. Grounded / Calibrated Confidence Scoring
* **What was discussed:** Calculating confidence objectively using hard facts:
  * Bonus for passing symbolic/retrieval verification.
  * Penalty for requiring retries or having missing steps.
  * Threshold trigger: If score $< 0.70$, set `needs_teacher_check = True`.
* **Prototype behavior:** The LLM solver node outputs its own raw self-reported confidence score (float `0.0` to `1.0`).

---

## 5. Orchestration & Streaming Pipeline
* **What was discussed:**
  * Global paper metadata extractor (subject, class level, board standard).
  * Question dispatcher using LangGraph's `Send` API for parallel question processing.
  * SSE stream emitter pushing `event: solution` and `event: progress` to Role 3.
* **Prototype behavior:** Evaluates a single question at a time through the inner graph.
