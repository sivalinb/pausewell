import re
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langsmith import tracing_context
from .models import Preferences, Reply
from .provider import choose_action
from .resources import CARDS, retrieve, RESOURCES


class State(TypedDict, total=False):
    reply: Reply
    prefs: Preferences
    result: dict
    action: str
    usage: dict
    route: str
    nodes: list[str]


def guard(state: State):
    r = state["reply"]
    # Notes remain local and ephemeral. Matching is conservative, never a clinical triage claim.
    note = r.note.casefold()
    urgent = re.search(
        r"chest (pain|pressure)|can.t breathe|cannot breathe|faint(ed|ing)?|severe.*breath|stroke", note
    )
    crisis = re.search(r"suicid|kill myself|end my life|hurt myself|self.harm", note)
    if r.symptoms == "urgent" or urgent:
        result = {
            "status": "urgent_support",
            "message": "These symptoms need prompt medical attention. Contact local emergency services now if symptoms are severe, sudden, or ongoing. In the US, call 911. Do not rely on this app to assess an emergency.",
            "cards": [],
            "resources": [RESOURCES["nimh-help"]],
        }
    elif r.symptoms == "crisis" or crisis:
        result = {
            "status": "crisis_support",
            "message": "You deserve immediate support. In the US, call or text 988 to reach a crisis counselor. If you may act now or are in immediate danger, call 911 or your local emergency number. Reach out to someone you trust who can stay with you.",
            "cards": [],
            "resources": [RESOURCES["nimh-help"]],
        }
    elif r.choice in {"skip", "snooze"}:
        result = {
            "status": r.choice,
            "message": "Of course. You decide when to check in.",
            "cards": [],
            "resources": [],
        }
    elif r.context == "exercise":
        result = {
            "status": "exercise",
            "message": "Thanks for correcting the context. We will pause prompts for recovery.",
            "cards": [],
            "resources": [],
        }
    elif r.context == "illness":
        result = {
            "status": "support",
            "message": "The watch cannot explain why you feel unwell. Consider contacting a health professional if symptoms concern you, persist, or worsen.",
            "cards": [],
            "resources": [RESOURCES["nimh-help"]],
        }
    elif r.feeling == "okay" and r.choice == "suggest":
        result = {
            "status": "okay",
            "message": "Thanks for checking. A change in readings does not mean you are stressed. No action needed.",
            "cards": [],
            "resources": [],
        }
    else:
        return {"route": "select", "nodes": ["guard"]}
    return {"result": result, "route": "finish", "nodes": ["guard"]}


def select(state: State):
    r, p = state["reply"], state["prefs"]
    allowed = ["name", "breathe"]
    if p.movement_ok:
        allowed.append("move")
    if not p.fluid_restriction:
        allowed.append("hydrate")
    fallback = {"tired": "move", "frustrated": "breathe", "worried": "name", "overwhelmed": "name"}.get(
        r.feeling, "name"
    )
    action = r.choice if r.choice in allowed else fallback if fallback in allowed else "name"
    usage = {"status": "user_choice", "provider": "local", "tokens": 0, "latency_ms": 0}
    if r.choice == "suggest":
        usage = choose_action(r.feeling, r.context, allowed, p.provider, p.cloud_consent)
        action = usage["action"] or action
    return {"action": action, "usage": usage, "nodes": state["nodes"] + ["select"]}


def ground(state: State):
    action = state["action"]
    return {
        "result": {
            "status": "offered",
            "message": "You know your day best. Choose what feels useful, or skip.",
            "cards": [{"id": action, **CARDS[action]}],
            "resources": retrieve(action),
            "model": state["usage"],
        },
        "nodes": state["nodes"] + ["retrieve", "validate"],
    }


builder = StateGraph(State)
builder.add_node("guard", guard)
builder.add_node("select", select)
builder.add_node("ground", ground)
builder.add_edge(START, "guard")
builder.add_conditional_edges("guard", lambda s: s["route"], {"select": "select", "finish": END})
builder.add_edge("select", "ground")
builder.add_edge("ground", END)
GRAPH = builder.compile()


def coach(reply: Reply, prefs: Preferences):
    # Disable inherited auto-tracing: graph state contains an ephemeral private note.
    # Only our explicit synthetic-only telemetry boundary may export information.
    with tracing_context(enabled=False):
        state = GRAPH.invoke({"reply": reply, "prefs": prefs})
    return {**state["result"], "nodes": state["nodes"], "prompt_version": "choice-v1"}
