"""Real NeMo 0.24 local custom rails; no model, judge, tool or network executor.

These narrow deterministic actions are supplementary scope checks. They do not
validate clinical truth or replace the independent exact quotation validator.
Each execution owns its NeMo runtime so conversation caches cannot cross users.
"""

import asyncio
import base64
import binascii
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
import json
import logging
import os
from pathlib import Path
import re
import threading
import time
import unicodedata

# Enforced before importing NeMo: its released package otherwise reports usage.
os.environ["NEMO_GUARDRAILS_NO_USAGE_STATS"] = "1"
os.environ["DISABLE_NEST_ASYNCIO"] = "true"

from langsmith import tracing_context  # noqa: E402
from nemoguardrails import RailsConfig  # noqa: E402
from nemoguardrails.actions import action  # noqa: E402
from nemoguardrails.actions.rail_outcome import RailOutcome  # noqa: E402
from nemoguardrails.rails.llm.llmrails import LLMRails  # noqa: E402
from nemoguardrails.rails.llm.options import RailStatus, RailType  # noqa: E402

from .evidence import instruction_like, SECTIONS  # noqa: E402

# NeMo can log raw conversation events and action exception details. Application
# telemetry receives only the bounded metadata below, never vendor event logs.
_vendor_log = logging.getLogger("nemoguardrails")
_vendor_log.addHandler(logging.NullHandler())
_vendor_log.propagate = False
_vendor_log.setLevel(logging.CRITICAL)

ENGINE = "nemo_guardrails"
MODE = "local_custom_actions"
POLICY_VERSION = "visitprep-nemo-v1"
RAIL_TIMEOUT_SECONDS = 2.0
# Bounded outstanding work prevents an uncooperative/faulty runtime from creating
# unlimited threads or queued private payloads. Normal async timeouts cancel work.
_WORKERS = ThreadPoolExecutor(max_workers=4, thread_name_prefix="visitprep-rail")
_SLOTS = threading.BoundedSemaphore(4)
_CONFIG_DIR = Path(__file__).with_name("rails")
_CONFIG_YAML = (_CONFIG_DIR / "config.yml").read_text()
_CONFIG_COLANG = (_CONFIG_DIR / "flows.co").read_text()

_INPUT_OVERRIDE = re.compile(
    r"\b(?:ignore|bypass|override|disable)\b.{0,65}\b(?:guardrails?|safety|polic(?:y|ies)|rules|restrictions|instructions)\b|"
    r"\b(?:you are|act as|pretend to be)\s+(?:now\s+)?(?:an?\s+)?(?:unrestricted|unfiltered|doctor|physician)\b|"
    r"\b(?:reveal|retrieve|show|print|export|send|access)\b.{0,65}\b(?:another|other|all)\s+(?:patients?|users?|people)(?:'s|s')?\b|"
    r"\b(?:execute|run|call|invoke)\b.{0,40}\b(?:shell|command|tool|python|curl|http|function)\b",
    re.I,
)
_CLINICAL_COMMAND = re.compile(
    r"\b(?:diagnose|prescribe)\s+(?:me|a|an|the|this|our|my|their|his|her|it|now)\b|"
    r"\b(?:give|tell|provide|recommend)\s+(?:me\s+)?(?:the\s+|a\s+|an\s+)?(?:exact\s+)?(?:diagnosis|dose|dosage|treatment)\b|"
    r"\b(?:tell|instruct|order)\b.{0,45}\b(?:stop|start|double|increase|decrease)\b.{0,40}\b(?:medication|medicine|tablets?|drug)\b",
    re.I,
)


def enabled_by_default():
    """Only server configuration can disable rails; unknown values fail enabled."""
    return os.environ.get("VISITPREP_NEMO_ENABLED", "true").strip().lower() not in {"0", "false", "off"}


def _normalized(value):
    return "".join(c for c in unicodedata.normalize("NFKC", value) if unicodedata.category(c) != "Cf")


def _input_reason(question):
    checked = _normalized(question)
    if instruction_like(checked) or _INPUT_OVERRIDE.search(checked):
        return "instruction_override"
    if _CLINICAL_COMMAND.search(checked):
        return "clinical_advice_request"
    # Inspect one bounded explicit Base64 request, never execute or recursively
    # decode it. Encodings without a detected instruction remain a known limit.
    if re.search(r"\b(?:decode|base64)\b", checked, re.I):
        for token in re.findall(r"[A-Za-z0-9+/]{16,}={0,2}", checked)[:4]:
            if len(token) > 1400:
                continue
            try:
                decoded = base64.b64decode(token, validate=True).decode("utf-8")
            except (ValueError, UnicodeError, binascii.Error):
                continue
            decoded = _normalized(decoded)
            if instruction_like(decoded) or _INPUT_OVERRIDE.search(decoded) or _CLINICAL_COMMAND.search(decoded):
                return "encoded_instruction_override"
    return None


def _output_reason(content, sources):
    try:
        value = json.loads(content)
    except (ValueError, TypeError):
        return "invalid_model_json"
    if not isinstance(value, dict) or set(value) != {"facts"}:
        return "output_schema_scope"
    facts = value["facts"]
    if not isinstance(facts, list) or not 1 <= len(facts) <= 8:
        return "output_schema_scope"
    for fact in facts:
        if not isinstance(fact, dict) or set(fact) != {"record_id", "quote", "section"}:
            return "output_schema_scope"
        if any(type(item) is not str for item in fact.values()) or not 4 <= len(fact["quote"]) <= 300:
            return "output_schema_scope"
        if fact["record_id"] not in sources or fact["section"] != sources[fact["record_id"]]:
            return "output_source_scope"
        # A medication imperative may be an attributed historical quotation.
        # Only model-directed instructions are blocked here; exact quotation is
        # independently checked by evidence.validate_selection afterward.
        if instruction_like(fact["quote"]):
            return "output_instruction_scope"
    return None


async def _execute_rail(stage, payload):
    """Fault-injection seam: actual NeMo check_async dispatch, no model calls.

    Tests/evaluators may replace this coroutine with one that raises or waits.
    This is below the timeout/error adapter and never a caller-controlled hook.
    """
    if stage == "input":
        content = payload["question"]
        sources = {}
    elif stage == "output":
        try:
            content = json.dumps(payload["selection"], ensure_ascii=False, allow_nan=False)
        except (ValueError, TypeError):
            content = "__invalid_json__"
        sources = {record["id"]: SECTIONS[record["kind"]] for record in payload["records"]}
    else:
        raise ValueError("Invalid rail stage")
    observed = []

    @action(name="visitprep_input_scope", is_system_action=True)
    async def input_action(context=None):
        reason = _input_reason(context["user_message"])
        observed.append(("blocked" if reason else "passed", reason or "input_scope_passed"))
        return RailOutcome.block(reason=reason) if reason else RailOutcome.allow()

    @action(name="visitprep_output_scope", is_system_action=True)
    async def output_action(context=None):
        reason = _output_reason(context["bot_message"], sources)
        observed.append(("blocked" if reason else "passed", reason or "output_scope_passed"))
        return RailOutcome.block(reason=reason) if reason else RailOutcome.allow()

    # New configuration AND runtime per call: no cached private events, shared
    # conversation histories, registered per-request data, or action state.
    rails = LLMRails(RailsConfig.from_content(yaml_content=_CONFIG_YAML, colang_content=_CONFIG_COLANG))
    rails.register_action(input_action)
    rails.register_action(output_action)
    try:
        result = await rails.check_async(
            [{"role": "user" if stage == "input" else "assistant", "content": content}],
            rail_types=[RailType.INPUT if stage == "input" else RailType.OUTPUT],
        )
        # Do not accept a library 'pass' if the configured local action failed to
        # execute, or if the runtime unexpectedly transformed private content.
        if len(observed) != 1:
            raise RuntimeError("Configured action did not execute exactly once")
        expected = RailStatus.PASSED if observed[0][0] == "passed" else RailStatus.BLOCKED
        if result.status != expected:
            raise RuntimeError("Runtime and action verdict disagree")
        return observed[0]
    finally:
        rails.events_history_cache.clear()
        rails._explain_info = None


def _run(stage, payload):
    with tracing_context(enabled=False):
        return asyncio.run(asyncio.wait_for(_execute_rail(stage, payload), timeout=RAIL_TIMEOUT_SECONDS))


def _notify(check, observer):
    if observer is not None:
        try:
            observer(dict(check))
        except Exception:
            # Observability cannot authorize content, affect fallback, or leak
            # a private callback exception into a response/vendor logger.
            pass
    return check


def skipped_check(stage, reason_code, observer=None):
    now = time.time_ns()
    return _notify({"stage": stage, "outcome": "skipped", "reason_code": reason_code,
                    "latency_ms": 0.0, "started_at_ns": now, "ended_at_ns": now}, observer)


def check_rail(stage, payload, *, observer=None):
    started_at = time.time_ns()
    started = time.perf_counter()
    if not _SLOTS.acquire(blocking=False):
        outcome, reason = "error", "runtime_busy"
    else:
        try:
            future = _WORKERS.submit(_run, stage, payload)
        except Exception:
            _SLOTS.release()
            outcome, reason = "error", "runtime_error"
        else:
            # The slot is released only when work actually ends, including work
            # that ignores cancellation. There is no unbounded pending queue.
            future.add_done_callback(lambda _: _SLOTS.release())
            try:
                outcome, reason = future.result(timeout=RAIL_TIMEOUT_SECONDS + 0.1)
            except (FutureTimeout, TimeoutError):
                future.cancel()
                outcome, reason = "timeout", "runtime_timeout"
            except Exception:
                outcome, reason = "error", "runtime_error"
    return _notify({"stage": stage, "outcome": outcome, "reason_code": reason,
                    "latency_ms": round((time.perf_counter() - started) * 1000, 3),
                    "started_at_ns": started_at, "ended_at_ns": time.time_ns()}, observer)


def metadata(enabled, checks):
    return {"engine": ENGINE, "mode": MODE if enabled else "disabled", "policy_version": POLICY_VERSION,
            "status": ("disabled" if not enabled else
                       "fallback" if any(c["outcome"] in {"blocked", "error", "timeout"} for c in checks)
                       else "passed"), "checks": checks}
