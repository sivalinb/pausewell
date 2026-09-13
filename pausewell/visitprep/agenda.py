"""Escaped patient-reviewed agenda exports; no scripts or external resources."""

import re
from datetime import datetime, timezone
from html import escape

# Root may authorize this exact fixed stylesheet with a CSP hash. There are no
# record-derived selectors, style values, script blocks or external resources.
PRINT_CSS = """
body{font:15px/1.5 system-ui,sans-serif;color:#183b37;background:#fff;margin:32px auto;padding:0 24px;max-width:780px}
h1{font-size:30px;margin-bottom:4px}h2{font-size:19px;margin-top:28px;border-bottom:1px solid #bfd1cd;padding-bottom:6px}
h3{font-size:16px;margin-bottom:8px}ol{padding-left:24px}li{margin:9px 0}blockquote{margin:10px 0;padding:8px 16px;border-left:3px solid #9ab6ad}
.muted{color:#496862;font-size:13px}.notice{padding:12px;background:#eef4f1;border:1px solid #c9dbd3}.source{font-size:12px;color:#496862}
.difference{margin:16px 0;break-inside:avoid}.quotation{break-inside:avoid}footer{margin-top:30px;font-size:12px;color:#496862}
@media print{body{margin:0;max-width:none;padding:0;font-size:11pt}h1{font-size:21pt}h2{font-size:14pt}a{color:inherit;text-decoration:none}.notice{background:none}blockquote{padding-top:3px;padding-bottom:3px}}
@page{margin:16mm}
"""


def markdown_escape(value):
    plain = escape(str(value).replace("\n", " "), quote=False)
    return re.sub(r"([\\`*_{}\[\]()#+.!>|-])", r"\\\1", plain)


def approval_time(agenda):
    return (
        datetime.fromisoformat(agenda["approved_at"]).astimezone(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    )


def _coverage_text(brief):
    coverage = brief.get("evidence_coverage")
    if not coverage:
        return "Selected evidence only; this older brief does not contain detailed selection counts."
    return (
        f"The brief contains {coverage['selected_excerpt_count']} quotations. "
        f"Including separately shown differences, {coverage['included_excerpt_count']} of "
        f"{coverage['eligible_excerpt_count']} eligible passages are shown from "
        f"{coverage['selected_record_count']} selected records. "
        f"{coverage['omitted_eligible_excerpt_count']} eligible passages are not shown. "
        "These counts do not measure clinical importance or completeness."
    )


def agenda_markdown(packet):
    brief, agenda = packet["brief"], packet["agenda"]
    lines = [
        "# Appointment agenda",
        "",
        markdown_escape(brief["patient"]["name"]),
        "",
        f"Reviewed by the person preparing this agenda: {approval_time(agenda)} · revision {agenda['revision']}",
        "",
        packet["notice"],
        "",
        "## My top priorities",
        "",
    ]
    lines.extend(f"{index}. {markdown_escape(value)}" for index, value in enumerate(agenda["priorities"], 1))
    if not agenda["priorities"]:
        lines.append("No priorities entered.")
    lines.extend(["", "## My questions for the visit", ""])
    lines.extend(f"{index}. {markdown_escape(value)}" for index, value in enumerate(agenda["questions"], 1))
    if not agenda["questions"]:
        lines.append("No questions entered.")
    lines.extend(["", "## Selected historical record quotations", "", _coverage_text(brief), ""])
    for fact in brief["facts"]:
        lines.extend(
            [
                f"**{markdown_escape(fact['source_title'])} · {fact['source_date']}**",
                "",
                "> " + markdown_escape(fact["quote"]),
                "",
                "Source ID: " + markdown_escape(fact["record_id"]),
                "",
            ]
        )
    if brief.get("recorded_differences"):
        lines.extend(["## Different dated entries to review", ""])
        for difference in brief["recorded_differences"]:
            lines.extend(["### " + markdown_escape(difference["label"]), "", difference["notice"], ""])
            for item in difference["items"]:
                lines.extend(
                    [
                        f"**{markdown_escape(item['source_title'])} · {item['source_date']}**",
                        "",
                        "> " + markdown_escape(item["quote"]),
                        "",
                        "Source ID: " + markdown_escape(item["record_id"]),
                        "",
                    ]
                )
    lines.extend(
        [
            "",
            agenda["approval_notice"],
            "",
            "Prepared with Pausewell. Not a diagnosis or a complete medical reconciliation.",
            "",
        ]
    )
    return "\n".join(lines)


def agenda_html(packet):
    brief, agenda = packet["brief"], packet["agenda"]

    def text(value):
        return escape(str(value), quote=True)

    def listed(items, empty):
        return (
            "<ol>" + "".join("<li>" + text(item) + "</li>" for item in items) + "</ol>"
            if items
            else "<p>" + empty + "</p>"
        )

    def quotation(fact):
        return (
            '<div class="quotation"><p class="source">'
            + text(fact["source_title"])
            + " · "
            + text(fact["source_date"])
            + "</p><blockquote>"
            + text(fact["quote"])
            + '</blockquote><p class="source">Source ID: '
            + text(fact["record_id"])
            + "</p></div>"
        )

    body = (
        "<h1>Appointment agenda</h1><p>"
        + text(brief["patient"]["name"])
        + '</p><p class="muted">'
        + "Reviewed by the person preparing this agenda: "
        + text(approval_time(agenda))
        + " · revision "
        + text(agenda["revision"])
        + '</p><p class="notice">'
        + text(packet["notice"])
        + "</p>"
        + "<h2>My top priorities</h2>"
        + listed(agenda["priorities"], "No priorities entered.")
        + "<h2>My questions for the visit</h2>"
        + listed(agenda["questions"], "No questions entered.")
        + '<h2>Selected historical record quotations</h2><p class="muted">'
        + text(_coverage_text(brief))
        + "</p>"
        + "".join(quotation(fact) for fact in brief["facts"])
    )
    if brief.get("recorded_differences"):
        body += "<h2>Different dated entries to review</h2>"
        for difference in brief["recorded_differences"]:
            body += (
                '<section class="difference"><h3>'
                + text(difference["label"])
                + '</h3><p class="muted">'
                + text(difference["notice"])
                + "</p>"
            )
            body += "".join(quotation(item) for item in difference["items"]) + "</section>"
    body += (
        "<footer>"
        + text(agenda["approval_notice"])
        + "<p>Prepared with Pausewell. Not a diagnosis or a complete medical reconciliation.</p></footer>"
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Appointment agenda</title><style>'
        + PRINT_CSS
        + "</style></head><body>"
        + body
        + "</body></html>"
    )
