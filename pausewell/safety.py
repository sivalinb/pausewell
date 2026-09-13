"""Bounded local support routing, not a general emergency detector.

Explicit support selections win. Text handling is supplementary and is evaluated
for both missed phrases and overblocking; unrecognized language remains possible.
"""

import re
import unicodedata
from .resources import RESOURCES

SUPPORT = {
    "urgent_support": "These symptoms need prompt medical attention. Contact local emergency services now if symptoms are severe, sudden, or ongoing. In the US, call 911. Do not rely on this app to assess an emergency.",
    "crisis_support": "You deserve immediate support. In the US, call or text 988 to reach a crisis counselor. If you may act now or are in immediate danger, call 911 or your local emergency number. Reach out to someone you trust who can stay with you.",
}
URGENT = re.compile(
    r"\bchest\s+(?:pain|pressure)\b|\b(?:can't|cannot|can not)\s+breathe\b|"
    r"\b(?:fainted|fainting)\b|\bsevere\s+(?:shortness of breath|breathlessness|trouble breathing)\b|"
    r"\bi\s+(?:think\s+i(?:'m| am)\s+having|am having|have signs of)\s+(?:a\s+)?stroke\b"
)
CRISIS = re.compile(
    r"\b(?:kill|hurt)\s+myself\b|\bend\s+my\s+life\b|\bend\s+it\s+all\b|"
    r"\bself[- ]?harm\b|\bsuicid(?:e|al)\b"
)
NEGATION = re.compile(
    r"\b(?:no|not|never|without|don't have|do not have|don't)\s+"
    r"(?:(?:any|current|signs of|thoughts of|thinking about|having|want to)\s+){0,3}$"
)


def normalize(note):
    text = unicodedata.normalize("NFKC", note).casefold().replace("’", "'")
    text = "".join(c for c in text if unicodedata.category(c) not in {"Cf", "Cc"} or c.isspace())
    # Normalize deliberate letter spacing, not arbitrary encodings or unknown languages.
    text = re.sub(r"\b(?:[a-z][ \t]+){2,}[a-z]\b", lambda m: re.sub(r"\s", "", m[0]), text)
    return re.sub(r"\s+", " ", text)


def relevant_match(pattern, text):
    for match in pattern.finditer(text):
        prefix = text[max(0, match.start() - 100) : match.start()]
        if NEGATION.search(prefix):
            continue
        # Only skip a clearly attributed fictional quotation. Unquoted personal
        # disclosures and explicit selectors still route to support.
        fictional = False
        for quote in re.finditer(r"""["“]([^"”]*)["”]|(?<!\w)'(.+?)'(?!\w)""", text):
            if quote.start() < match.start() and match.end() < quote.end():
                attribution = text[max(0, quote.start() - 90) : quote.start()]
                fiction = re.search(
                    r"\b(?:in (?:my|a|the) novel|(?:writing|wrote) (?:a |the |my )?fictional (?:story|novel))\b",
                    attribution,
                )
                speaker = re.search(r"\b(?:a|the) character (?:says|said)\s*[:,-]?\s*$", attribution)
                negated = fiction and re.search(r"\b(?:not|never)\s*$", attribution[: fiction.start()])
                if fiction and speaker and not negated:
                    fictional = True
        if fictional:
            continue
        return True
    return False


def support_result(reply):
    # A direct human selection cannot be overridden by text or cached state.
    if reply.symptoms in {"urgent", "crisis"}:
        status = reply.symptoms + "_support"
    else:
        note = normalize(reply.note)
        status = (
            "urgent_support"
            if relevant_match(URGENT, note)
            else "crisis_support"
            if relevant_match(CRISIS, note)
            else None
        )
    if status is None:
        return None
    return {
        "status": status,
        "message": SUPPORT[status],
        "cards": [],
        "resources": [RESOURCES["nimh-help"]],
        "safety_policy": "support-v2",
        "nodes": ["guard"],
    }
