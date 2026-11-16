
# import json
# from pathlib import Path
# from operator import eq, ge, le, gt, lt

# ROOT = Path(__file__).resolve().parent.parent
# SCHEMES_FILE = ROOT / "data" / "schemes.json"

# OPERATORS = {
#     "eq": eq,
#     "gte": ge,
#     "lte": le,
#     "gt": gt,
#     "lt": lt,
# }


# def _load_schemes():
#     with open(SCHEMES_FILE, encoding="utf-8") as f:
#         return json.load(f)


# def evaluate_condition(condition, profile):
#     """
#     Evaluate one explicitly configured eligibility condition.

#     Supported operators: eq, gte, lte, gt, lt, in, truthy.
#     """

#     field = condition.get("field")
#     operator = condition.get("operator")
#     expected = condition.get("value")

#     if not field or not operator:
#         return "unknown", "Invalid eligibility rule configuration."

#     actual = profile.get(field)

#     if actual is None or actual == "":
#         return "unknown", f"Missing profile information: {field}"

#     try:
#         if operator in OPERATORS:
#             passed = OPERATORS[operator](actual, expected)

#         elif operator == "in":
#             passed = actual in expected

#         elif operator == "truthy":
#             passed = bool(actual) == bool(expected)

#         else:
#             return "unknown", f"Unsupported operator: {operator}"

#         description = condition.get(
#             "description",
#             f"{field} {operator} {expected}"
#         )

#         return (
#             ("satisfied", description)
#             if passed
#             else ("not_satisfied", description)
#         )

#     except (TypeError, ValueError):
#         return "unknown", f"Could not evaluate condition for {field}"


# def check_eligibility(scheme_id, user_profile):
#     """
#     Preliminary deterministic eligibility assessment.

#     Only evaluates rules explicitly configured in schemes.json.
#     Missing or unverified rules remain unknown.
#     """

#     schemes = _load_schemes()

#     scheme = next(
#         (s for s in schemes if s.get("scheme_id") == scheme_id),
#         None
#     )

#     if scheme is None:
#         return {
#             "scheme_id": scheme_id,
#             "status": "unknown",
#             "satisfied": [],
#             "not_satisfied": [],
#             "unknown": ["Scheme not found."]
#         }

#     profile = user_profile or {}
#     rules = scheme.get("eligibility_rules", [])

#     if not rules:
#         return {
#             "scheme_id": scheme_id,
#             "scheme_name": scheme.get("scheme_name"),
#             "status": "unknown",
#             "satisfied": [],
#             "not_satisfied": [],
#             "unknown": [
#                 "Verified machine-readable eligibility rules "
#                 "have not been configured for this scheme."
#             ],
#             "disclaimer": (
#                 "Preliminary guidance only. Final eligibility "
#                 "is determined by the government authority."
#             )
#         }

#     satisfied = []
#     not_satisfied = []
#     unknown = []

#     for rule in rules:
#         result, description = evaluate_condition(rule, profile)

#         if result == "satisfied":
#             satisfied.append(description)

#         elif result == "not_satisfied":
#             not_satisfied.append(description)

#         else:
#             unknown.append(description)

#     if not_satisfied:
#         status = "not_satisfied"
#     elif unknown:
#         status = "unknown"
#     else:
#         status = "satisfied"

#     return {
#         "scheme_id": scheme_id,
#         "scheme_name": scheme.get("scheme_name"),
#         "status": status,
#         "satisfied": satisfied,
#         "not_satisfied": not_satisfied,
#         "unknown": unknown,
#         "disclaimer": (
#             "This is a preliminary rule-based assessment, "
#             "not an official eligibility decision."
#         )
#     }
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMES_FILE = ROOT / "data" / "schemes.json"


def _load_schemes():
    with open(SCHEMES_FILE, encoding="utf-8") as f:
        return json.load(f)


def _compare(actual, operator, expected):
    if operator == "eq": return actual == expected
    if operator == "gte": return actual >= expected
    if operator == "lte": return actual <= expected
    if operator == "gt": return actual > expected
    if operator == "lt": return actual < expected
    if operator == "in": return actual in expected
    if operator == "truthy": return bool(actual)
    raise ValueError(f"Unsupported eligibility operator: {operator}")


def check_eligibility(scheme_id, user_profile):
    """Return a conservative preliminary result; missing/unverified facts stay unknown."""
    scheme = next((s for s in _load_schemes() if s["scheme_id"] == scheme_id), None)
    disclaimer = (
        "Preliminary guidance only. This is not an official eligibility decision; "
        "the relevant government authority/database makes the final determination."
    )
    if scheme is None:
        return {"scheme_id": scheme_id, "status": "unknown", "satisfied": [],
                "not_satisfied": [], "unknown": ["Scheme rules are not configured."],
                "disclaimer": disclaimer}

    rules = scheme.get("eligibility_rules")
    if not rules or not rules.get("conditions"):
        return {"scheme_id": scheme_id, "status": "unknown", "satisfied": [],
                "not_satisfied": [],
                "unknown": ["Verified decision rules are not configured for this scheme."],
                "disclaimer": disclaimer}

    profile = user_profile or {}
    satisfied, not_satisfied, unknown = [], [], []
    for condition in rules["conditions"]:
        field = condition["field"]
        reason = condition.get("reason", field)
        actual = profile.get(field)
        if actual is None or actual == "":
            unknown.append(f"Please provide/verify: {field}. {reason}")
            continue
        try:
            passed = _compare(actual, condition["operator"], condition["value"])
        except (TypeError, ValueError):
            unknown.append(f"Could not safely evaluate: {field}. {reason}")
            continue
        (satisfied if passed else not_satisfied).append(reason)

    # A failed mandatory condition is a negative preliminary signal; missing facts are still disclosed.
    if not_satisfied:
        status = "not_satisfied"
    elif unknown:
        status = "unknown"
    else:
        status = "satisfied"

    notes = rules.get("notes")
    if notes:
        unknown.append(f"Important limitation: {notes}")
    return {"scheme_id": scheme_id, "scheme_name": scheme.get("scheme_name"),
            "status": status, "satisfied": satisfied,
            "not_satisfied": not_satisfied, "unknown": unknown,
            "disclaimer": disclaimer}
