"""Register an authenticated, single-owner appointment-preparation workspace."""

import json
import re
import time
from html import escape as escape_html
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from .fixtures import PATIENT, PATIENT_ID, display_patient
from .agenda import agenda_html, agenda_markdown
from .graph import make_brief
from .models import BriefRequest, RecordInput, AgendaInput
from .provider import configured
from .store import VisitPrepStore, AccessDenied, CapacityExceeded, AgendaConflict
from .telemetry import VisitPrepTelemetry

SCOPE_NOTICE = (
    "Seed demo records are authored fictional; imported record identity is not verified. Prepare a cited, extractive appointment brief; "
    "this tool does not diagnose, interpret results or recommend treatment. Selected evidence is not complete medical reconciliation. "
    "Imported records, saved briefs and patient agendas remain on your server until deleted. Cloud processing requires new record-text consent on every request."
)


def markdown_brief(brief):
    def escape(value):
        plain = escape_html(value.replace("\n", " "), quote=False)
        return re.sub(r"([\\`*_{}\[\]()#+.!>|-])", r"\\\1", plain)

    lines = [
        "# Appointment preparation",
        "",
        brief["message"],
        "",
        brief.get(
            "quotation_notice", "These are historical record quotations, not current treatment instructions."
        ),
        "",
        "## Selected source excerpts",
        "",
    ]
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
    if brief.get("recorded_differences"):
        lines += ["", "## Different dated entries to review", ""]
        for difference in brief["recorded_differences"]:
            lines += ["### " + escape(difference["label"]), "", difference["notice"], ""]
            for item in difference["items"]:
                lines += [
                    f"**{escape(item['source_title'])} · {item['source_date']}**",
                    "",
                    "> " + escape(item["quote"]),
                    "",
                ]
    if brief.get("evidence_coverage"):
        coverage = brief["evidence_coverage"]
        lines += ["", "## Selection coverage", "", coverage["notice"], ""]
        for row in coverage["records"]:
            lines.append(
                f"- {escape(row['title'])}: {row['included_count']} of {row['eligible_count']} eligible passages shown; {row['omitted_count']} not shown; {row['excluded_count']} excluded by text rules."
            )
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
        except AgendaConflict as exc:
            telemetry.record(operation, exc.outcome, (time.perf_counter() - started) * 1000)
            raise HTTPException(409, str(exc)) from None

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

    @router.get("/briefs/{brief_id}/agenda")
    def get_agenda(brief_id: str):
        start = time.perf_counter()
        result = guarded("agenda_read", lambda: store.get_agenda(brief_id))
        telemetry.record("agenda_read", "read", (time.perf_counter() - start) * 1000)
        return result

    @router.put("/briefs/{brief_id}/agenda")
    def save_agenda(brief_id: str, value: AgendaInput):
        # Patient-authored words stay in owner-local storage, outside the model
        # and telemetry. Approval always applies to the submitted revision.
        start = time.perf_counter()
        operation = "agenda_approve" if value.approved else "agenda_save"
        result = guarded(operation, lambda: store.save_agenda(brief_id, value))
        telemetry.record(
            operation, "approved" if value.approved else "saved", (time.perf_counter() - start) * 1000
        )
        return result

    @router.get("/briefs/{brief_id}/agenda/export")
    def export_agenda(brief_id: str, format: Literal["json", "markdown", "html"] = "html"):
        start = time.perf_counter()
        packet = guarded("agenda_export", lambda: store.agenda_export(brief_id))
        renderers = {
            "html": agenda_html,
            "markdown": agenda_markdown,
            "json": lambda value: json.dumps(value, indent=2, ensure_ascii=False),
        }
        content = renderers[format](packet)
        telemetry.record("agenda_export", "exported", (time.perf_counter() - start) * 1000)
        media_type, extension = {
            "html": ("text/html", "html"),
            "markdown": ("text/markdown", "md"),
            "json": ("application/json", "json"),
        }[format]
        return Response(
            content,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="pausewell-appointment-agenda.{extension}"',
                "X-Agenda-Revision": str(packet["agenda"]["revision"]),
            },
        )

    @router.get("/observability")
    def observability():
        return telemetry.snapshot()

    @router.delete("/data")
    def erase():
        store.erase()
        telemetry.clear()
        return {
            "deleted": True,
            "scope": "VisitPrep records, saved briefs, patient agendas and local operation telemetry",
        }

    @router.post("/demo/reset")
    def reset_demo():
        start = time.perf_counter()
        guarded("reset", store.reset_demo)
        telemetry.record("reset", "reset", (time.perf_counter() - start) * 1000, synthetic=True)
        return {"restored": True, "patient": PATIENT}

    app.include_router(router)
    return router
