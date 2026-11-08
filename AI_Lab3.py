import json
from typing import List, Dict, Any, Tuple
import operator
import streamlit as st
 
OPS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "in": lambda a, b: a in b,
    "not_in": lambda a, b: a not in b,
}
 
DEFAULT_RULES: List[Dict[str, Any]] = [
    {
        "name": "Top merit candidate",
        "priority": 100,
        "conditions": [
            ["cgpa", ">=", 3.7],
            ["co_curricular_score", ">=", 80],
            ["family_income", "<=", 8000],
            ["disciplinary_actions", "==", 0],
        ],
        "action": {
            "decision": "AWARD_FULL",
            "reason": "Excellent academic & co-curricular performance, with acceptable need",
        },
    },
    {
        "name": "Good candidate - partial scholarship",
        "priority": 80,
        "conditions": [
            ["cgpa", ">=", 3.3],
            ["co_curricular_score", ">=", 60],
            ["family_income", "<=", 12000],
            ["disciplinary_actions", "<=", 1],
        ],
        "action": {
            "decision": "AWARD_PARTIAL",
            "reason": "Good academic & involvement record with moderate need",
        },
    },
    {
        "name": "Need-based review",
        "priority": 70,
        "conditions": [
            ["cgpa", ">=", 2.5],
            ["family_income", "<=", 4000],
        ],
        "action": {
            "decision": "REVIEW",
            "reason": "High need but borderline academic score",
        },
    },
    {
        "name": "Low CGPA – not eligible",
        "priority": 95,
        "conditions": [
            ["cgpa", "<", 2.5],
        ],
        "action": {
            "decision": "REJECT",
            "reason": "CGPA below minimum scholarship requirement",
        },
    },
    {
        "name": "Serious disciplinary record",
        "priority": 90,
        "conditions": [
            ["disciplinary_actions", ">=", 2],
        ],
        "action": {
            "decision": "REJECT",
            "reason": "Too many disciplinary records",
        },
    },
]
 
def evaluate_condition(facts: Dict[str, Any], cond: List[Any]) -> bool:
    """Evaluate a single condition: [field, op, value]."""
    if len(cond) != 3:
        return False
    field, op, value = cond
    if field not in facts or op not in OPS:
        return False
    try:
        return OPS[op](facts[field], value)
    except Exception:
        return False
 
def rule_matches(facts: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    """All conditions must be true (AND)."""
    return all(evaluate_condition(facts, c) for c in rule.get("conditions", []))
 
def run_rules(facts: Dict[str, Any], rules: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Returns (best_action, fired_rules)
    - best_action: chosen by highest priority among fired rules (ties keep the first encountered)
    - fired_rules: list of rule dicts that matched, sorted by priority desc
    """
    fired = [r for r in rules if rule_matches(facts, r)]
    if not fired:
        return ({"decision": "REVIEW", "reason": "No rule matched"}, [])
 
    fired_sorted = sorted(fired, key=lambda r: r.get("priority", 0), reverse=True)
    best = fired_sorted[0].get("action", {"decision": "REVIEW", "reason": "No action"})
    return best, fired_sorted
 
# ----------------------------
# 2) Streamlit UI
# ----------------------------
# Helpers for displaying results (they only read the rules; the engine above is unchanged)
SYMBOL = {">=": "≥", "<=": "≤", "==": "=", "!=": "≠", ">": ">", "<": "<", "in": "in", "not_in": "not in"}
 
def condition_checks(facts: Dict[str, Any], rule: Dict[str, Any]) -> List[Dict[str, str]]:
    """One row per condition: what the rule needs, what the applicant has, and whether it is true."""
    rows = []
    for cond in rule.get("conditions", []):
        field, op, value = (list(cond) + [None, None, None])[:3]
        actual = facts.get(field, "missing")
        rows.append({
            "Condition": f"{field} {SYMBOL.get(op, op)} {value}",
            "Applicant value": f"{actual:g}" if isinstance(actual, float) else str(actual),
            "Result": "✅ True" if evaluate_condition(facts, cond) else "❌ False",
        })
    return rows
 
st.set_page_config(page_title="Scholarship Rule-Based System", page_icon="🎓", layout="wide")
st.title("🎓 Scholarship Advisory — Rule-Based System")
st.caption("BSD3513 LAB REPORT 3 | MOK KER QIN SD24032")
st.caption("Enter the applicant's facts in the sidebar and click **Evaluate**. "
           "Rules can be viewed or edited in the **Rules** tab.")
 
# Sidebar: applicant facts + Evaluate button only
with st.sidebar:
    st.header("Applicant Facts")
    cgpa = st.number_input("Cumulative GPA (CGPA)", min_value=0.0, max_value=4.0, step=0.01, value=3.50, format="%.2f")
    family_income = st.number_input("Monthly family income (RM)", min_value=0, step=100, value=5000)
    co_curricular_score = st.number_input("Co-curricular involvement score (0–100)", min_value=0, max_value=100, step=1, value=70)
    community_service_hours = st.number_input("Community service hours", min_value=0, step=1, value=40)
    current_semester = st.number_input("Current semester of study", min_value=1, max_value=14, step=1, value=3)
    disciplinary_actions = st.number_input("Number of disciplinary actions", min_value=0, step=1, value=0)
    run = st.button("Evaluate", type="primary", width="stretch")
 
facts = {
    "cgpa": float(cgpa),
    "family_income": float(family_income),
    "co_curricular_score": int(co_curricular_score),
    "community_service_hours": int(community_service_hours),
    "current_semester": int(current_semester),
    "disciplinary_actions": int(disciplinary_actions),
}
 
tab_eval, tab_rules = st.tabs(["Evaluate", "Rules"])
 
# ---- Rules tab: JSON editor (fall back to defaults if invalid) ----
with tab_rules:
    st.subheader("Rules (JSON)")
    st.caption("Keep the default Lab 3 rules or paste your own JSON array of rules, then click **Evaluate** again.")
    default_json = json.dumps(DEFAULT_RULES, indent=2, ensure_ascii=False)
    rules_text = st.text_area("Edit rules here", value=default_json, height=450)
    try:
        rules = json.loads(rules_text)
        assert isinstance(rules, list), "Rules must be a JSON array"
        st.success(f"{len(rules)} rules loaded.")
    except Exception as e:
        st.error(f"Invalid rules JSON. Using defaults. Details: {e}")
        rules = DEFAULT_RULES
 
# ---- Evaluate tab ----
with tab_eval:
    st.subheader("Applicant Facts")
    row1 = st.columns(3)
    row1[0].metric("CGPA", f"{facts['cgpa']:.2f}", border=True)
    row1[1].metric("Monthly family income", f"RM {facts['family_income']:,.0f}", border=True)
    row1[2].metric("Co-curricular score", f"{facts['co_curricular_score']} / 100", border=True)
    row2 = st.columns(3)
    row2[0].metric("Community service hours", facts["community_service_hours"], border=True)
    row2[1].metric("Current semester", facts["current_semester"], border=True)
    row2[2].metric("Disciplinary actions", facts["disciplinary_actions"], border=True)
 
    st.divider()
 
    if run:
        action, fired = run_rules(facts, rules)
        badge = action.get("decision", "REVIEW")
        reason = action.get("reason", "-")
        winner = fired[0].get("name", "(unnamed)") if fired else "None (no rule matched)"
 
        # Decision banner
        st.subheader("Decision")
        banner = f"### {badge}\n{reason}\n\nWinning rule: **{winner}**"
        if badge == "AWARD_FULL":
            st.success(banner)
        elif badge == "AWARD_PARTIAL":
            st.info(banner)
        elif badge == "REJECT":
            st.error(banner)
        else:
            st.warning(banner)
 
        # Matched rules
        st.subheader("Matched Rules (by priority)")
        if not fired:
            st.info("No rules matched, so the applicant is sent for manual review.")
        else:
            st.dataframe(
                [{"Rank": i, "Rule": r.get("name", "(unnamed)"), "Priority": r.get("priority", 0),
                  "Decision": r.get("action", {}).get("decision", "-"),
                  "Reason": r.get("action", {}).get("reason", "-")}
                 for i, r in enumerate(fired, start=1)],
                hide_index=True, width="stretch",
            )
 
        # Feature: why each rule was or was not matched
        st.subheader("Why? Rule-by-rule check")
        st.caption("A rule is matched only when ALL of its conditions are true.")
        for r in sorted(rules, key=lambda r: r.get("priority", 0), reverse=True):
            matched = rule_matches(facts, r)
            label = f"{'✅ Matched' if matched else '❌ Not matched'} — {r.get('name', '(unnamed)')} (priority {r.get('priority', 0)})"
            with st.expander(label, expanded=matched):
                st.dataframe(condition_checks(facts, r), hide_index=True, width="stretch")
                st.caption(f"THEN → {r.get('action', {}).get('decision', '-')}: {r.get('action', {}).get('reason', '-')}")
    else:
        st.info("Set input values in the sidebar and click **Evaluate**.")
 
