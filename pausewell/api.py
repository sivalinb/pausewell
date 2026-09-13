import json
import base64
import hashlib
import os
import secrets
import time
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from .models import Window, Reply, Preferences, Feedback, utcnow
from .store import Store
from .signals import assess
from .coach import coach
from .resources import RESOURCES
from .demo import fixture, SCENARIOS
from .telemetry import Telemetry
from .safety import support_result
from .visitprep.agenda import PRINT_CSS

ROOT = Path(__file__).resolve().parent.parent
PRINT_STYLE_HASH = base64.b64encode(hashlib.sha256(PRINT_CSS.encode()).digest()).decode()


def create_app(db_path=None, token=None, clock=utcnow):
    load_dotenv(ROOT / ".env")
    token = token or os.getenv("PAUSEWELL_TOKEN", "")
    if len(token) < 32 or token.startswith("replace-with"):
        raise RuntimeError("Set PAUSEWELL_TOKEN to a random value of at least 32 characters")
    app = FastAPI(title="Pausewell", docs_url=None, redoc_url=None, openapi_url=None)
    store = Store(db_path or os.getenv("PAUSEWELL_DB", str(ROOT / "data/pausewell.sqlite")))
    telemetry = Telemetry()
    app.state.store = store
    app.state.telemetry = telemetry

    async def auth(request: Request):
        header = request.headers.get("authorization", "")
        if not secrets.compare_digest(header, "Bearer " + token):
            raise HTTPException(401, "Enter your local access token")

    @app.middleware("http")
    async def protect(request, call_next):
        # Read with a bound even for chunked transfers, before Pydantic parses JSON.
        if request.method in {"POST", "PUT"}:
            size = 0
            chunks = []
            async for chunk in request.stream():
                size += len(chunk)
                if size > 64000:
                    return JSONResponse({"detail": "Request too large"}, status_code=413)
                chunks.append(chunk)
            request._body = b"".join(chunks)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            f"default-src 'self'; script-src 'self'; style-src 'self' 'sha256-{PRINT_STYLE_HASH}'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"
        )
        return response

    @app.exception_handler(RequestValidationError)
    async def invalid(request, exc):
        # Do not echo rejected health payloads in errors.
        return JSONResponse(
            {"detail": "Invalid input. Check fields, timestamps, and ranges."}, status_code=422
        )

    @app.get("/healthz")
    def health():
        return {"status": "ok", "version": "0.1.0"}

    @app.get("/api/resources", dependencies=[Depends(auth)])
    def resources():
        return RESOURCES

    @app.get("/api/preferences", dependencies=[Depends(auth)])
    def preferences():
        return store.prefs()

    @app.put("/api/preferences", dependencies=[Depends(auth)])
    def update_preferences(prefs: Preferences):
        store.save_prefs(prefs)
        return prefs

    def process(window):
        start = time.perf_counter()
        result = store.ingest(window, assess(window, clock()), clock())
        telemetry.record(
            "ingest",
            result,
            (time.perf_counter() - start) * 1000,
            window.source == "synthetic",
            store.prefs().synthetic_traces,
        )
        return result

    @app.post("/api/windows", dependencies=[Depends(auth)])
    def ingest(window: Window):
        return process(window)

    @app.post("/api/demo/{scenario}", dependencies=[Depends(auth)])
    def demo(scenario: str):
        if scenario not in SCENARIOS:
            raise HTTPException(404, "Unknown scenario")
        window = fixture(scenario, clock())
        return {"window": window, "result": process(window)}

    @app.post("/api/checkins/{checkin_id}/reply", dependencies=[Depends(auth)])
    def respond(checkin_id: str, reply: Reply):
        # Fresh safety needs must not be hidden by a completed/expired/missing ID.
        # No persistence or cloud call; this branch also works after a user skips.
        support_start = time.perf_counter()
        immediate = support_result(reply)
        if immediate:
            telemetry.record(
                "support",
                immediate,
                (time.perf_counter() - support_start) * 1000,
                synthetic=False,
                enabled=False,
            )
            return immediate
        # Serialize reply completion: retries never duplicate a paid model call.
        with store.lock:
            row = store.get(checkin_id)
            if not row:
                raise HTTPException(404, "Check-in not found")
            if row["status"] != "pending":
                return {**json.loads(row["result"]), "duplicate": True}
            from datetime import datetime, timedelta

            if clock() - datetime.fromisoformat(row["at"]) > timedelta(hours=2):
                raise HTTPException(409, "This check-in has expired")
            start = time.perf_counter()
            prefs = store.prefs()
            result = coach(reply, prefs)
            store.complete(checkin_id, result, clock())
            result["trace"] = telemetry.record(
                "coach",
                result,
                (time.perf_counter() - start) * 1000,
                row["source"] == "synthetic",
                prefs.synthetic_traces,
            )
            return result

    @app.post("/api/support", dependencies=[Depends(auth)])
    def support(reply: Reply):
        start = time.perf_counter()
        result = support_result(reply)
        if result is None:
            return {
                "status": "support_options",
                "message": "Choose urgent medical help or crisis support. You can also open the public resources without signing in.",
                "cards": [],
                "resources": [RESOURCES["nimh-help"]],
            }
        telemetry.record(
            "support", result, (time.perf_counter() - start) * 1000, synthetic=False, enabled=False
        )
        return result

    @app.post("/api/checkins/{checkin_id}/feedback", dependencies=[Depends(auth)])
    def feedback(checkin_id: str, value: Feedback):
        if not store.get(checkin_id):
            raise HTTPException(404, "Check-in not found")
        store.feedback(checkin_id, value)
        return {"saved": True}

    @app.get("/api/history", dependencies=[Depends(auth)])
    def history():
        return store.export(clock())

    @app.delete("/api/data", dependencies=[Depends(auth)])
    def erase():
        store.erase()
        telemetry.clear()
        app.state.visitprep_store.erase()
        app.state.visitprep_telemetry.clear()
        return {
            "deleted": True,
            "scope": "Local app records and settings. Apple Health and remote synthetic traces are separate.",
        }

    @app.get("/api/observability", dependencies=[Depends(auth)])
    def observe():
        return telemetry.snapshot()

    @app.get("/metrics", dependencies=[Depends(auth)], response_class=PlainTextResponse)
    def metrics():
        counts = telemetry.snapshot()["counters"]
        return "\n".join(f"pausewell_{k}_total {v}" for k, v in counts.items()) + "\n"

    @app.get("/")
    def home():
        return FileResponse(ROOT / "web/index.html")

    from .visitprep import register_visitprep

    record_db = Path(store.path).with_name(Path(store.path).stem + "-visitprep.sqlite")
    register_visitprep(app, auth, record_db)

    app.mount("/static", StaticFiles(directory=ROOT / "web"), name="static")
    app.mount("/art", StaticFiles(directory=ROOT / "docs/assets"), name="art")
    return app
