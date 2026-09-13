"""Small reviewed public corpus. Source text is paraphrased, not model-fetched."""

RESOURCES = {
    "nimh-self-care": {
        "title": "NIMH · Caring for your mental health",
        "url": "https://www.nimh.nih.gov/health/topics/caring-for-your-mental-health",
        "reviewed": "2026-09-12",
        "summary": "Small amounts of activity, hydration, restful routines and social connection can support well-being.",
    },
    "nhs-breathing": {
        "title": "NHS · Breathing exercises for stress",
        "url": "https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/breathing-exercises-for-stress/",
        "reviewed": "2026-09-12",
        "summary": "Find a comfortable position and breathe gently without forcing your breath.",
    },
    "nhs-stress": {
        "title": "NHS · Understanding stress",
        "url": "https://www.nhs.uk/mental-health/feelings-symptoms-behaviours/feelings-and-symptoms/stress/",
        "reviewed": "2026-09-12",
        "summary": "Notice what feels difficult and seek support when coping is becoming hard.",
    },
    "nimh-help": {
        "title": "NIMH · Getting help",
        "url": "https://www.nimh.nih.gov/health/find-help",
        "reviewed": "2026-09-12",
        "summary": "Find professional support and crisis resources.",
    },
}
CARDS = {
    "move": {
        "title": "Make a little room to move",
        "text": "If it feels comfortable and safe, try a brief walk or a gentle seated stretch. You can stop or skip at any time.",
        "source_ids": ["nimh-self-care"],
    },
    "hydrate": {
        "title": "Pause for a sip",
        "text": "If you would like some water, take a small sip. Follow any fluid guidance from your care team. This is a reminder, not a finding of dehydration.",
        "source_ids": ["nimh-self-care"],
    },
    "name": {
        "title": "Put a word to the moment",
        "text": "Try completing: ‘I notice I feel ___. What I need next might be ___.’ Unsure is a valid answer. This optional reflection is an app exercise.",
        "source_ids": ["nhs-stress"],
    },
    "breathe": {
        "title": "Find a comfortable breath",
        "text": "Settle into a comfortable position and let your breathing be gentle and unforced. Skip this if focusing on breathing feels uncomfortable.",
        "source_ids": ["nhs-breathing"],
    },
}


def retrieve(action: str) -> list[dict]:
    return [{"id": k, **RESOURCES[k]} for k in CARDS[action]["source_ids"]]
