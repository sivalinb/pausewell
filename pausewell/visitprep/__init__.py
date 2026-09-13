"""Register an authenticated, single-owner appointment-preparation workspace."""

import json
import re
import time
from html import escape as escape_html
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from .fixtures import PATIENT, PATIENT_ID, display_patient
from .graph import make_brief
from .models import BriefRequest, RecordInput
from .provider import configured
from .store import VisitPrepStore, AccessDenied, CapacityExceeded
from .telemetry import VisitPrepTelemetry

SCOPE_NOTICE = (
    "Seed demo records are authored fictional; imported record identity is not verified. Prepare a cited, extractive appointment brief; "
    "this tool does not diagnose, interpret results or recommend treatment. Selected evidence is not complete medical reconciliation. "
    "Imported records and saved briefs remain on your server until deleted. Cloud processing requires new record-text consent on every request."
)


def markdown_brief(brief):
    def escape(value):
        plain = escape_html(value.replace("\n", " "), quote=False)
        return re.sub(r"([\\`*_{}\[\]()#+.!>|-])", r"\\\1", plain)

    lines = ["# Appointment preparation", "", brief["message"], "", "## Selected source excerpts", ""]
    for fact in brief["facts"]:
        lines += [
            f"**{escape(fact['source_title'])} · {fact['source_date']}**",
            "",
            f"> {escape(fact['quote'])}",
            "",
            f"Source ID: {escape(fact['record_id'])}",
            "",
        ]
    lines += ["## Questions for the clinician", ""]
    lines += ["- " + question["text"] for question in brief["questions"]]
    lines += ["", "Selected evidence only. Not a complete medical reconciliation.", ""]
    return "\n".join(lines)


def register_visitprep(app, auth, db_path):
    store = VisitPrepStore(db_path)
    telemetry = VisitPrepTelemetry()
    app.state.visitprep_store = store
    app.state.visitprep_telemetry = telemetry
    router = APIRouter(prefix="/api/visitprep", dependencies=[Depends(auth)])

    def guarded(operation, callback):
        started = time.perf_counter()
        try:
            return callback()
        except AccessDenied:
            telemetry.record(operation, "blocked_authorization", (time.perf_counter() - started) * 1000)
            raise HTTPException(404, "Record, patient or brief unavailable") from None
        except CapacityExceeded as exc:
            telemetry.record(operation, "capacity_limit", (time.perf_counter() - started) * 1000)
            raise HTTPException(422, str(exc)) from None

    @router.get("/bootstrap")
    def bootstrap():
        records = store.list_records()
        return {
            "patient": display_patient(records),
            "records": records,
            "providers": [
                {"id": provider, "configured": configured(provider)}
                for provider in ["local", "nebius", "fireworks"]
            ],
            "consent": {"record_text_cloud": False},
            "scope_notice": SCOPE_NOTICE,
            "provenance": "authored_synthetic_demo; imports are user-supplied and not independently verified",
        }

    @router.get("/records")
    def records(patient_id: str = Query(default=PATIENT_ID, max_length=80)):
        records = guarded("read", lambda: store.list_records(patient_id))
        return {"patient": display_patient(records), "records": records}

    @router.post("/records", status_code=201)
    def add_record(value: RecordInput):
        start = time.perf_counter()
        record = guarded("import", lambda: store.add_record(value))
        telemetry.record(
            "import", "saved", (time.perf_counter() - start) * 1000, synthetic=record["synthetic"]
        )
        return record

    @router.delete("/records/{record_id}")
    def delete_record(record_id: str):
        start = time.perf_counter()
        guarded("delete", lambda: store.delete_record(record_id))
        telemetry.record("delete", "deleted", (time.perf_counter() - start) * 1000)
        return {"deleted": True, "derived_briefs_deleted": True}

    @router.post("/brief")
    def brief(request: BriefRequest):
        start = time.perf_counter()
        result = guarded("brief", lambda: make_brief(store, request))
        telemetry.record(
            "brief",
            result["model"]["status"],
            (time.perf_counter() - start) * 1000,
            model=result["model"],
            synthetic=result["synthetic"],
        )
        return result

    @router.get("/briefs")
    def briefs():
        return {"briefs": store.briefs()}

    @router.get("/briefs/{brief_id}")
    def get_brief(brief_id: str):
        return guarded("read", lambda: store.get_brief(brief_id))

    @router.get("/briefs/{brief_id}/export")
    def export_brief(brief_id: str, format: Literal["json", "markdown"] = "json"):
        result = guarded("read", lambda: store.get_brief(brief_id))
        data = (
            json.dumps(result, indent=2, ensure_ascii=False) if format == "json" else markdown_brief(result)
        )
        extension = "json" if format == "json" else "md"
        return Response(
            data,
            media_type="application/json" if format == "json" else "text/markdown",
            headers={"Content-Disposition": f'attachment; filename="pausewell-visitprep-brief.{extension}"'},
        )

    @router.get("/observability")
    def observability():
        return telemetry.snapshot()

    @router.delete("/data")
    def erase():
        store.erase()
        telemetry.clear()
        return {"deleted": True, "scope": "VisitPrep records, saved briefs and local operation telemetry"}

    @router.post("/demo/reset")
    def reset_demo():
        start = time.perf_counter()
        guarded("reset", store.reset_demo)
        telemetry.record("reset", "reset", (time.perf_counter() - start) * 1000, synthetic=True)
        return {"restored": True, "patient": PATIENT}

    app.include_router(router)
    return router
