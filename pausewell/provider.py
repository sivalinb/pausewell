"""LLM chooses from reviewed actions. It cannot author user-visible health claims."""

import json
import os
import time
import httpx

ENDPOINTS = {
    "nebius": "https://api.tokenfactory.nebius.com/v1/chat/completions",
    "fireworks": "https://api.fireworks.ai/inference/v1/chat/completions",
}


def choose_action(feeling, context, allowed, provider, consent, transport=None):
    result = {"action": None, "status": "disabled", "provider": "local", "tokens": 0, "latency_ms": 0}
    if not consent or provider == "local":
        return result
    key = os.getenv(provider.upper() + "_API_KEY")
    model = os.getenv(provider.upper() + "_MODEL")
    if provider not in ENDPOINTS or not key or not model:
        return {**result, "status": "not_configured"}
    # Strictly enum-only payload: no note, biometrics, timestamps, IDs, or history.
    payload = {
        "model": model,
        "temperature": 0,
        "max_tokens": 100,
        "messages": [
            {
                "role": "system",
                "content": "Select one optional wellness action from the allowed list. Never diagnose. Return only JSON with exactly one key: action. The person can skip. This is preference routing, not medical assessment.",
            },
            {
                "role": "user",
                "content": json.dumps({"feeling": feeling, "context": context, "allowed": allowed}),
            },
        ],
        "response_format": {"type": "json_object"},
    }
    start = time.perf_counter()
    try:
        with httpx.Client(timeout=12, follow_redirects=False, transport=transport) as client:
            response = client.post(
                ENDPOINTS[provider], headers={"Authorization": f"Bearer {key}"}, json=payload
            )
            response.raise_for_status()
            body = response.json()
        choice = body["choices"][0]
        selected = json.loads(choice["message"]["content"])
        if (
            choice.get("finish_reason") != "stop"
            or set(selected) != {"action"}
            or selected["action"] not in allowed
        ):
            raise ValueError("Unapproved model output")
        tokens = body.get("usage", {}).get("total_tokens", 0)
        return {
            "action": selected["action"],
            "status": "accepted",
            "provider": provider,
            "tokens": tokens if type(tokens) is int and tokens >= 0 else 0,
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
        }
    except Exception:
        # Never log exception bodies: providers may echo prompts or authorization material.
        return {
            **result,
            "status": "fallback",
            "provider": provider,
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
        }
