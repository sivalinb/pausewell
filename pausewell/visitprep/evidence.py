"""Exact source excerpts; no generated clinical interpretations."""

import re
import unicodedata

SECTIONS = {
    "visit": "timeline",
    "medication": "medications",
    "lab": "labs",
    "allergy": "allergies",
    "other": "other",
}
QUESTION_TEMPLATES = {
    "medications": "Can we reconcile these medication entries and confirm which list is current?",
    "labs": "What do these recorded results mean in my clinical context, and is any follow-up needed?",
    "allergies": "Is this allergy entry complete, including the reaction and when it happened?",
    "timeline": "What should we follow up from these prior visits?",
    "other": "Is this record relevant to the appointment, and what should we clarify?",
}
# This supplementary filter limits obvious instruction copying. It is not an
# injection detector or the authorization boundary; all documents remain data.
INSTRUCTION_LIKE = re.compile(
    r"\b(?:ignore|disregard)\b|system\s*(?:override|prompt|message)|"
    r"\b(?:assistant|developer)\b|api[_ -]?key|bearer\s|password|https?://|"
    r"\b(?:return|output)\s*(?:only|json|\{)|\b(?:print|reveal|echo)\b|"
    r"\b(?:execute|curl|diagnose|prescribe)\b|\b(?:you must|you should|you are)\b|"
    r"\b(?:double|increase|decrease)\b.{0,35}\b(?:dose|dosage)\b|"
    r"\b(?:stop|start) taking\b|\b(?:export|send|reveal|print)\b.{0,50}\b(?:record|secret|patient|token)\b",
    re.I,
)


def excerpts(record):
    """Return bounded source-preserving spans, excluding obvious instructions."""
    candidates = []
    for line in record["text"].splitlines():
        line = line.strip()
        parts = [line] if len(line) <= 300 else re.split(r"(?<=[.!?])\s+", line)
        for part in parts:
            checked = unicodedata.normalize("NFKC", part)
            checked = "".join(c for c in checked if unicodedata.category(c) != "Cf")
            if 4 <= len(part) <= 300 and not INSTRUCTION_LIKE.search(checked):
                if part not in candidates:
                    candidates.append(part)
            if len(candidates) >= 8:
                return candidates
    return candidates


def local_evidence(records):
    # Round-robin preserves coverage of distinct records before adding detail.
    choices = [(record, excerpts(record)) for record in records]
    facts = []
    for index in range(8):
        for record, quotes in choices:
            if index < len(quotes):
                facts.append(
                    {"record_id": record["id"], "quote": quotes[index], "section": SECTIONS[record["kind"]]}
                )
            if len(facts) == 8:
                return {"facts": facts}
    return {"facts": facts}


def validate_selection(payload, records):
    if not isinstance(payload, dict) or set(payload) != {"facts"}:
        raise ValueError("Invalid selection schema")
    facts = payload["facts"]
    if not isinstance(facts, list) or not 1 <= len(facts) <= 8:
        raise ValueError("Invalid fact count")
    known = {record["id"]: record for record in records}
    seen = set()
    validated = []
    for fact in facts:
        if not isinstance(fact, dict) or set(fact) != {"record_id", "quote", "section"}:
            raise ValueError("Invalid fact schema")
        if any(type(fact[key]) is not str for key in fact):
            raise ValueError("Invalid fact type")
        record = known.get(fact["record_id"])
        if record is None or fact["section"] != SECTIONS[record["kind"]]:
            raise ValueError("Unknown source or section")
        if fact["quote"] not in excerpts(record):
            raise ValueError("Quote is not an allowed exact source excerpt")
        key = (fact["record_id"], fact["quote"])
        if key in seen:
            raise ValueError("Duplicate evidence")
        seen.add(key)
        validated.append({**fact, "source_title": record["title"], "source_date": record["date"]})
    return validated
