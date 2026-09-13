"""Exact source excerpts; no generated clinical interpretations."""

import re
import unicodedata
from collections import defaultdict
from hashlib import sha256

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
# Clinical/administrative imperatives can be genuine historical source content.
# This supplementary filter targets instructions addressed to the model, not
# words such as "print", "disregard", or "increase" in isolation.
MODEL_DIRECTIVE = re.compile(
    r"(?:^|\s)(?:system\s*(?:override|prompt|message)|developer\s*(?:message|instruction)?|assistant)\s*[:>]|"
    r"\b(?:to|for)\s+(?:the\s+)?(?:ai|assistant|chatbot|language model|llm)\s*[:;,]|"
    r"\b(?:ai|assistant|chatbot|language model|llm)\s*[:,]\s*(?:ignore|obey|follow|trust|return|output|print|reveal|send|upload|export|diagnose)|"
    r"\b(?:return|output)\s+(?:only\s+)?(?:json|\{)|"
    r"\b(?:ignore|disregard|override)\b.{0,50}\b(?:schema|system prompt|developer message)\b|"
    r"\b(?:reveal|print|echo|send|export|upload)\b.{0,70}\b(?:api[_ -]?key|system prompt|secret|bearer token|other patient|all patients)\b|"
    r"\b(?:before|when)\s+(?:preparing|writing|generating|returning)\s+(?:the\s+)?(?:brief|summary|response)\b.{0,80}\b(?:ignore|obey|override|reveal|diagnose|prescribe)\b",
    re.I,
)
PRIOR_INSTRUCTIONS = re.compile(
    r"\b(?:ignore|disregard|override)\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions|rules|prompts)\b",
    re.I,
)
HISTORICAL_ATTRIBUTION = re.compile(
    r"\b(?:clinician|doctor|dr\.?\s+\w+|nurse|pharmacist|patient)\b.{0,65}\b(?:said|stated|reported|advised|instructed|documented|recorded|requested|was told)\b|"
    r"\b(?:historical|prior|past|recorded)\s+(?:note|plan|instruction|advice)\b",
    re.I,
)


def instruction_like(text):
    checked = unicodedata.normalize("NFKC", text)
    checked = "".join(c for c in checked if unicodedata.category(c) != "Cf")
    if MODEL_DIRECTIVE.search(checked):
        return True
    # Unattributed overrides are model instructions; attributed clinical history
    # remains quoted history unless it explicitly addresses model authority.
    return bool(PRIOR_INSTRUCTIONS.search(checked) and not HISTORICAL_ATTRIBUTION.search(checked))


def excerpt_inventory(record):
    """Count inspected passages and exclusions without hiding the evidence cap."""
    candidates = []
    excluded_instruction_count = excluded_length_count = duplicate_count = 0
    for line in record["text"].splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [line] if len(line) <= 300 else re.split(r"(?<=[.!?])\s+", line)
        for part in parts:
            if instruction_like(part):
                excluded_instruction_count += 1
            elif not 4 <= len(part) <= 300:
                excluded_length_count += 1
            elif part in candidates:
                duplicate_count += 1
            else:
                candidates.append(part)
    return {
        "eligible": candidates,
        "excluded_instruction_count": excluded_instruction_count,
        "excluded_length_count": excluded_length_count,
        "duplicate_count": duplicate_count,
    }


def excerpts(record):
    """All eligible exact spans; the eight-fact brief cap is a separate limit."""
    return excerpt_inventory(record)["eligible"]


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
        validated.append(
            {
                **fact,
                "source_title": record["title"],
                "source_date": record["date"],
                "quotation_context": "historical_record_quote",
            }
        )
    return validated


def _medication_entry(quote):
    # Recognize text shape, not pharmacology. Only compare a named entry with a
    # recorded numeric strength; unknown formats receive no inferred match.
    text = re.sub(r"^(?:medication(?: list)?|medicines|meds)\s*:\s*", "", quote, flags=re.I)
    text = re.sub(
        r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s+(?:takes|was taking|is taking|reported taking)\s+", "", text
    )
    match = re.match(
        r"([A-Za-z][A-Za-z0-9 /-]{1,55}?)\s+(\d+(?:\.\d+)?\s*(?:mg|mcg|g|units|mL)\b.*)", text, re.I
    )
    if not match:
        return None
    name = " ".join(match[1].casefold().split())
    recorded_value = " ".join(match[2].casefold().rstrip(".").split())
    return name, recorded_value


def recorded_differences(records):
    """Flag differing exact entries across dated sources without resolving them."""
    grouped = defaultdict(list)
    for record in records:
        for quote in excerpts(record):
            if record["kind"] == "medication":
                entry = _medication_entry(quote)
                if entry:
                    grouped[("medication_entry_difference", entry[0])].append((record, quote, entry[1]))
            elif record["kind"] == "allergy" and re.search(r"\ballerg(?:y|ies|ic)\b|\bnkda\b", quote, re.I):
                grouped[("allergy_entry_difference", "allergy entries")].append(
                    (record, quote, " ".join(quote.casefold().split()))
                )
    differences = []
    for (kind, name), entries in grouped.items():
        if len({entry[0]["id"] for entry in entries}) < 2 or len({entry[0]["date"] for entry in entries}) < 2:
            continue
        if len({entry[2] for entry in entries}) < 2:
            continue
        unique = list({(record["id"], quote): (record, quote) for record, quote, _ in entries}.values())
        items = [
            {
                "record_id": record["id"],
                "quote": quote,
                "section": SECTIONS[record["kind"]],
                "source_title": record["title"],
                "source_date": record["date"],
                "quotation_context": "historical_record_quote",
            }
            for record, quote in sorted(unique, key=lambda entry: (entry[0]["date"], entry[0]["id"]))
        ]
        differences.append(
            {
                "id": sha256((kind + ":" + name).encode()).hexdigest()[:12],
                "kind": kind,
                "label": "Different recorded entries: " + name,
                "items": items,
                "method": "heuristic",
                "notice": "These dated source entries differ in wording. They may reflect changes or incomplete records; this tool does not decide which is current or correct.",
            }
        )
    return differences


def evidence_coverage(records, facts, differences, model_status):
    brief_keys = {(fact["record_id"], fact["quote"]) for fact in facts}
    difference_keys = {
        (item["record_id"], item["quote"]) for difference in differences for item in difference["items"]
    }
    included = brief_keys | difference_keys
    rows = []
    for record in records:
        inventory = excerpt_inventory(record)
        record_keys = {(record["id"], quote) for quote in inventory["eligible"]}
        rows.append(
            {
                "record_id": record["id"],
                "title": record["title"],
                "date": record["date"],
                "eligible_count": len(record_keys),
                "included_count": len(record_keys & included),
                "brief_fact_count": len(record_keys & brief_keys),
                "difference_excerpt_count": len(record_keys & difference_keys),
                "excluded_count": inventory["excluded_instruction_count"]
                + inventory["excluded_length_count"],
                "excluded_instruction_count": inventory["excluded_instruction_count"],
                "excluded_length_count": inventory["excluded_length_count"],
                "duplicate_count": inventory["duplicate_count"],
                "omitted_count": len(record_keys - included),
            }
        )
    return {
        "selection_method": "model_selected" if model_status == "accepted" else "local_round_robin",
        "selected_record_count": len(records),
        "cited_record_count": sum(row["brief_fact_count"] > 0 for row in rows),
        "evidence_record_count": sum(row["included_count"] > 0 for row in rows),
        "eligible_excerpt_count": sum(row["eligible_count"] for row in rows),
        "selected_excerpt_count": len(brief_keys),
        "included_excerpt_count": len(included),
        "difference_excerpt_count": len(difference_keys),
        "omitted_eligible_excerpt_count": sum(row["omitted_count"] for row in rows),
        "uncited_record_ids": [row["record_id"] for row in rows if not row["included_count"]],
        "excluded_instruction_count": sum(row["excluded_instruction_count"] for row in rows),
        "excluded_length_count": sum(row["excluded_length_count"] for row in rows),
        "selection_limit": 8,
        "complete_reconciliation": False,
        "records": rows,
        "notice": "Counts describe this text-selection process, not clinical importance or completeness. Differences are separate exact evidence outside the eight-fact brief limit; omitted passages may still matter.",
    }
