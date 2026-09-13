"""Authorize → retrieve → select → validate → prepare, with no agent tools."""

import re
from datetime import datetime, timezone
from typing import TypedDict
from uuid import uuid4

from langgraph.graph import StateGraph, START, END
from langsmith import tracing_context

from .evidence import local_evidence, validate_selection, QUESTION_TEMPLATES
from .fixtures import display_patient
from .models import BriefRequest
from .provider import select_evidence
from .store import VisitPrepStore


class State(TypedDict, total=False):
    store: VisitPrepStore
    request: BriefRequest
    ids: list[str]
    records: list[dict]
    nodes: list[str]
    selection: dict
    facts: list[dict]
    usage: dict
    result: dict


def authorize(state):
    req = state["request"]
    ids = state["store"].authorized_ids(req.patient_id, req.record_ids)
    return {"ids": ids, "nodes": ["authorize"]}


def retrieve(state):
    records = state["store"].retrieve(state["request"].patient_id, state["ids"]) if state["ids"] else []
    return {"records": records, "nodes": state["nodes"] + ["retrieve"]}


def select(state):
    req, records = state["request"], state["records"]
    if not records:
        selected = {
            "payload": None,
            "model": {"provider": "local", "status": "no_records", "tokens": 0, "latency_ms": 0},
        }
    elif req.provider == "local":
        selected = {
            "payload": None,
            "model": {"provider": "local", "status": "local", "tokens": 0, "latency_ms": 0},
        }
    elif not req.cloud_consent:
        selected = {
            "payload": None,
            "model": {"provider": "local", "status": "consent_required", "tokens": 0, "latency_ms": 0},
        }
    else:
        selected = select_evidence(records, req.question, req.provider, req.cloud_consent)
    return {"selection": selected["payload"], "usage": selected["model"], "nodes": state["nodes"] + ["model"]}


def validate(state):
    model = dict(state["usage"])
    facts = []
    if state["selection"] is not None:
        try:
            facts = validate_selection(state["selection"], state["records"])
            model["status"] = "accepted"
        except (ValueError, TypeError, KeyError):
            model["status"] = "rejected_output"
    if not facts:
        fallback = local_evidence(state["records"])
        if fallback["facts"]:
            facts = validate_selection(fallback, state["records"])
    return {"facts": facts, "usage": model, "nodes": state["nodes"] + ["validate"]}


def prepare(state):
    facts = state["facts"]
    clinical_request = bool(
        re.search(
            r"diagnos|what disease|do i have|prescri|\b(?:dose|dosage|treatment|cure)\b|"
            r"should i.{0,35}(?:take|stop|increase|decrease)|"
            r"\b(?:stop|start|double|increase|decrease)\b.{0,35}\b(?:medication|medicine|drug|tablet)\b",
            state["request"].question,
            re.I,
        )
    )
    questions = []
    for section, template in QUESTION_TEMPLATES.items():
        ids = list(dict.fromkeys(fact["record_id"] for fact in facts if fact["section"] == section))
        if ids:
            questions.append({"text": template, "record_ids": ids})
    message = (
        (
            "This tool cannot diagnose, interpret results or recommend medication changes. "
            if clinical_request
            else ""
        )
        + "Selected excerpts from your records and questions to discuss with a clinician. This is not a complete medical reconciliation."
    )
    result = {
        "id": str(uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "patient": display_patient(state["records"]),
        "scope": "visit_preparation_only",
        "request_scope": "clinical_request_limited" if clinical_request else "visit_preparation",
        "message": message,
        "facts": facts,
        "questions": questions,
        "model": state["usage"],
        "coverage": {
            "selected_records": len(state["records"]),
            "selected_facts": len(facts),
            "complete_reconciliation": False,
        },
        "nodes": state["nodes"] + ["brief"],
        "synthetic": bool(state["records"]) and all(record["synthetic"] for record in state["records"]),
        "policy_version": "visitprep-v1",
    }
    state["store"].save_brief(result, state["ids"])
    return {"result": result}


builder = StateGraph(State)
for name, action in [
    ("authorize", authorize),
    ("retrieve", retrieve),
    ("model", select),
    ("validate", validate),
    ("brief", prepare),
]:
    builder.add_node(name, action)
builder.add_edge(START, "authorize")
for first, second in [
    ("authorize", "retrieve"),
    ("retrieve", "model"),
    ("model", "validate"),
    ("validate", "brief"),
]:
    builder.add_edge(first, second)
builder.add_edge("brief", END)
GRAPH = builder.compile()


def make_brief(store, request):
    # Graph state contains private record text/question. Disable inherited tracing.
    with tracing_context(enabled=False):
        return GRAPH.invoke({"store": store, "request": request})["result"]
