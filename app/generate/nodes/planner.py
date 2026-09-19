"""Planner Node: Analyzes the question and determines the specialized solver route."""

from typing import Dict, Any
from app.generate.state import QuestionState


def planner_node(state: QuestionState) -> Dict[str, Any]:
    """Inspects question type, options, and text to route to the appropriate solver.

    Routes:
    - 'mcq': If options exist or type is 'mcq'
    - 'math': If type is 'numerical' or question contains mathematical calculation cues
    - 'theory': For conceptual definitions and short/long descriptive questions
    """
    q_type = (state.get("type") or "").lower()
    options = state.get("options")
    text = (state.get("text") or "").lower()

    # 1. Check for Multiple Choice Question
    if options or q_type == "mcq":
        return {"selected_route": "mcq"}

    # 2. Check for Numerical / Mathematical problem
    math_cues = ["calculate", "find the value", "evaluate", "expansion of", "solve", "probability"]
    math_symbols = ["²", "³", "√", "+", "=", "×", "π", "ap whose", "0.9̄", "m s⁻²"]

    is_numerical_type = q_type == "numerical"
    has_math_cues = any(cue in text for cue in math_cues)
    has_math_symbols = any(sym in text for sym in math_symbols)

    if is_numerical_type or (has_math_cues and has_math_symbols):
        return {"selected_route": "math"}

    # 3. Default to Descriptive / Theory question
    return {"selected_route": "theory"}
