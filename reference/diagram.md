# Prototype Pipeline: Question Solve Engine

```text
               [Input: Question & Paper Metadata]
                               │
                               ▼
                        [Planner Node]
                               │
                   (Dynamic Routing by Type)
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
                 [Math]      [MCQ]     [Theory]
                [Solver]    [Solver]   [Solver]
                    │          │          │
                    └──────────┼──────────┘
                               │
                               ▼
                     [Contract Normalizer]
                               │
                               ▼
               [Output: Frozen API Solution JSON]
```

---

## 1. Prototype Scope

This prototype focuses on the core MVP question-solving loop without external verifiers or multimodal diagram processing:

* **`planner`**:
  * Ingests question text, marks, options, and paper metadata (e.g., subject, class level).
  * Classifies the question and routes it dynamically to one of the 3 core solvers.
* **`math_solver`**:
  * Solves numerical problems step-by-step.
  * Formulates formulas, steps, mark breakdown, common student calculation mistakes, and self-reports confidence.
* **`mcq_solver`**:
  * Evaluates options A, B, C, D.
  * Selects the correct option, explains the reasoning, identifies distractor traps, and self-reports confidence.
* **`theory_solver`**:
  * Solves short and long descriptive questions.
  * Provides structured point-by-point answers, mark allocation, key misconceptions, and self-reports confidence.
* **`contract_normalizer`**:
  * Maps the solver output into the frozen project API contract:
    * `question_number`
    * `answer`
    * `steps`
    * `mark_split`
    * `common_mistakes`
    * `confidence`
    * `verified_by: "none"` (since verifiers are deferred)
    * `needs_teacher_check: false` (or based on threshold)
