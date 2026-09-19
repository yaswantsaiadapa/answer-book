"""MCQ Solver Node: Solves multiple-choice and assertion-reason questions using Groq."""

from typing import Dict, Any
from app.generate.state import QuestionState
from app.llm.client import call_groq_json


def mcq_solver_node(state: QuestionState) -> Dict[str, Any]:
    """Evaluates options, applies process of elimination, and extracts distractor traps."""
    q_num = state.get("number", "")
    text = state.get("text", "")
    marks = state.get("marks", 1)
    options = state.get("options") or []
    metadata = state.get("metadata", {})
    subject = metadata.get("subject", "Science / Mathematics")
    grade = metadata.get("class", "Class 9")
    board = metadata.get("board", "CBSE")

    options_formatted = "\n".join(options) if options else "No options list provided."

    system_prompt = f"""You are an expert {board} {subject} teacher for {grade} students.
Your goal is to solve the multiple-choice question with high accuracy and explain student misconceptions.

Follow these strict rules:
1. The 'answer' must include BOTH the letter and text of the correct choice (e.g. '(D) 25x² + 20xy + 4y²').
2. In 'steps', provide a systematic explanation:
   - For Assertion-Reason: test Assertion (True/False), test Reason (True/False), then test the causal 'because' link.
   - For standard MCQs: state the governing identity/concept and show step-by-step why the selected option holds.
3. In 'mark_split', break down the {marks} mark(s). The sum of 'marks' must equal exactly {marks}.
4. In 'common_mistakes', inspect the INCORRECT options (distractors) and explain the exact trap or error that leads students to choose them.
5. Provide a 'confidence' score between 0.0 and 1.0.
6. Return ONLY valid JSON matching the schema below.
"""

    user_prompt = f"""Question Number: {q_num}
Total Marks: {marks}
Question:
{text}

Options:
{options_formatted}

Output JSON Schema:
{{
  "question_number": "{q_num}",
  "answer": "(<Letter>) <Option Text>",
  "steps": ["<step 1>", "<step 2>", ...],
  "mark_split": [
    {{"marks": {marks}, "for": "selecting correct option with proper justification"}}
  ],
  "common_mistakes": [
    {{"wrong": "(<Letter>) <Wrong Option>", "why": "<why student falls for this trap>"}}
  ],
  "confidence": <float 0.0 to 1.0>,
  "verified_by": "none",
  "needs_teacher_check": false
}}"""

    result = call_groq_json(system_prompt, user_prompt)
    result["question_number"] = q_num
    return {"raw_solution": result}
