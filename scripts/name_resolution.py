import difflib
from typing import List, Tuple, Optional, Dict

def resolve_name(input_name: str, candidates: List[str], min_ratio: float = 0.8) -> Dict:
    """
    Resolves a name against a list of candidates using exact, case-insensitive, partial, and fuzzy matching.
    Returns a dict with keys:
        - match: str or None
        - matches: list of all matches (if ambiguous)
        - suggestions: list of close matches (if no match)
        - warning: str (ambiguity or not found)
    """
    input_clean = input_name.strip().lower()
    candidates_clean = [c.strip().lower() for c in candidates]
    exact_matches = [c for c, orig in zip(candidates_clean, candidates) if input_clean == c]
    if exact_matches:
        idx = candidates_clean.index(exact_matches[0])
        return {"match": candidates[idx], "matches": [candidates[idx]], "suggestions": [], "warning": None}
    # Case-insensitive match
    ci_matches = [orig for c, orig in zip(candidates_clean, candidates) if input_clean == c]
    if ci_matches:
        return {"match": ci_matches[0], "matches": [ci_matches[0]], "suggestions": [], "warning": None}
    # Partial match
    partial_matches = [orig for c, orig in zip(candidates_clean, candidates) if input_clean in c or c in input_clean]
    if len(partial_matches) == 1:
        return {"match": partial_matches[0], "matches": [partial_matches[0]], "suggestions": [], "warning": None}
    if len(partial_matches) > 1:
        return {"match": None, "matches": partial_matches, "suggestions": [], "warning": f"Ambiguous: multiple matches for '{input_name}'"}
    # Fuzzy match
    close = difflib.get_close_matches(input_name, candidates, n=3, cutoff=min_ratio)
    if close:
        if len(close) == 1:
            return {"match": close[0], "matches": [close[0]], "suggestions": [], "warning": None}
        return {"match": None, "matches": close, "suggestions": close, "warning": f"Ambiguous: multiple fuzzy matches for '{input_name}'"}
    # No match
    suggestions = difflib.get_close_matches(input_name, candidates, n=3, cutoff=0.6)
    return {"match": None, "matches": [], "suggestions": suggestions, "warning": f"No match for '{input_name}'. Suggestions: {suggestions}"}
