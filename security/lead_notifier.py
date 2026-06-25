# security/lead_notifier.py

"""
Telegram alerting for commercial events (audit.html / advanced-audit.html
submissions, and any other "a human needs to know about this now" event).

Reuses the same proven pattern as the trading-system project's
core/notifications.py (Telegram Bot API sendMessage, token/chat_id from
env vars, 5s timeout) - this is a fresh, independent implementation for
Agentic Zero, not an import across projects, so this product's lead
alerts never share a bot/chat with the trading system's alerts.

Two gaps closed relative to the pattern being reused:

  1. Every notify_* function in the original always discards
     send_message()'s success/failure boolean - a failed Telegram send
     vanishes with nothing but a log line. Here, every failure is also
     logged to AuditLogger as a WARNING (or CRITICAL for
     notify_audit_submitted specifically, since a silently-lost lead
     notification is a real commercial cost, not just an observability
     nicety).

  2. The original calls requests.post() synchronously inline. If this
     were called directly inside a web request handler processing a form
     submission, the lead's browser would hang for up to 5 seconds waiting
     on a Telegram API round-trip before seeing a response. send_async()
     fires the actual HTTP call on a background thread so the caller
     (the form handler) can return immediately; the result is still
     captured and logged, just not synchronously awaited by the caller.
"""

from __future__ import annotations

import os
import re
import threading
from datetime import datetime, timezone
from typing import Any, Optional

import requests
from dotenv import load_dotenv

from security.audit_logger import AuditLogger

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

_audit_logger = AuditLogger()


def _safe_client_id(raw: str, fallback: str = "_unknown_lead") -> str:
    """company/contact name from a public web form is untrusted input.
    AuditLogger uses client_id directly as a filename component
    (security/state/audit_logs/<client_id>.jsonl) with no sanitization of
    its own - "../../etc/passwd" as a company name would otherwise be
    interpreted as a relative path escaping the intended audit_logs
    directory. Collapse to a safe slug here, at the point where untrusted
    input first enters this system, rather than touching audit_logger.py
    (already relied upon everywhere else with trusted, code-generated
    client_ids until now).
    """
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", (raw or "").strip())
    slug = slug.strip("_")[:80]
    return slug or fallback


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def send_message(text: str, *, silent: bool = False, timeout: int = 5) -> bool:
    """Synchronous send - same shape as the trading-system pattern. Use
    send_async() instead when calling from a request handler that must
    not block on Telegram's response time.
    """
    if not TOKEN or not CHAT_ID:
        _audit_logger.log(
            event_type="TELEGRAM_NOT_CONFIGURED",
            client_id="_platform",
            actor="lead_notifier",
            action="send_message",
            outcome="SKIPPED",
            severity="WARNING",
            reason="TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set in environment.",
            metadata={},
        )
        return False

    try:
        response = requests.post(
            f"{BASE_URL}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_notification": silent,
            },
            timeout=timeout,
        )
        ok = response.json().get("ok", False)
        if not ok:
            _audit_logger.log(
                event_type="TELEGRAM_SEND_FAILED",
                client_id="_platform",
                actor="lead_notifier",
                action="send_message",
                outcome="FAILED",
                severity="WARNING",
                reason=f"Telegram API responded ok=false: {response.text[:200]}",
                metadata={},
            )
        return ok
    except Exception as exc:
        _audit_logger.log(
            event_type="TELEGRAM_SEND_ERROR",
            client_id="_platform",
            actor="lead_notifier",
            action="send_message",
            outcome="ERROR",
            severity="WARNING",
            reason=str(exc),
            metadata={},
        )
        return False


def send_async(text: str, *, silent: bool = False, on_done: Optional[Any] = None) -> None:
    """Fire-and-forget: returns immediately, the actual HTTP call (and its
    audit logging) happens on a background thread. Use this from any web
    request handler - never block a form submission on Telegram's
    response time.
    """

    def _worker():
        ok = send_message(text, silent=silent)
        if on_done:
            try:
                on_done(ok)
            except Exception as exc:
                # on_done is typically an audit-logging callback - if THAT
                # fails, don't let it vanish silently like the path
                # traversal attempt did during testing. This print is a
                # deliberate last-resort fallback when the audit system
                # itself is the thing that broke.
                print(f"[lead_notifier] on_done callback raised: {exc}")

    threading.Thread(target=_worker, daemon=True).start()


def notify_audit_submitted(payload: dict[str, Any]) -> None:
    """Call this the moment an audit.html / advanced-audit.html submission
    is accepted by whatever backend ends up receiving it (Formspree
    webhook or a custom endpoint - this function doesn't care which).
    Fire-and-forget by design: a slow or failed Telegram send must never
    delay or break the form-submission response to the lead.
    """
    name = payload.get("contact_name", "Unknown")
    company = payload.get("company", "Unknown company")
    email = payload.get("contact_email", "")
    role = payload.get("contact_role", "")

    text = (
        f"🟢 <b>Nuevo Audit recibido</b>\n"
        f"👤 {name} — {role}\n"
        f"🏢 {company}\n"
        f"✉️ {email}\n"
        f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    )

    def _log_outcome(ok: bool):
        _audit_logger.log(
            event_type="AUDIT_LEAD_NOTIFICATION",
            client_id=_safe_client_id(company),
            actor="lead_notifier",
            action="notify_audit_submitted",
            outcome="SENT" if ok else "LOST",
            severity="INFO" if ok else "CRITICAL",
            reason=(
                "Lead notification delivered to Telegram."
                if ok
                else "Lead notification FAILED to deliver - check Telegram bot config "
                "and the TELEGRAM_SEND_FAILED/TELEGRAM_SEND_ERROR events above for why. "
                "The lead's submission was still accepted; only the alert was lost."
            ),
            metadata={"contact_email": email, "company": company},
        )

    send_async(text, on_done=_log_outcome)


def notify_advanced_audit_submitted(payload: dict[str, Any]) -> None:
    company = payload.get("company", "Unknown company")
    text = (
        f"🟢 <b>Advanced Audit completado</b>\n"
        f"🏢 {company}\n"
        f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    )

    def _log_outcome(ok: bool):
        _audit_logger.log(
            event_type="ADVANCED_AUDIT_LEAD_NOTIFICATION",
            client_id=_safe_client_id(company),
            actor="lead_notifier",
            action="notify_advanced_audit_submitted",
            outcome="SENT" if ok else "LOST",
            severity="INFO" if ok else "CRITICAL",
            reason="Lead notification delivered." if ok else "Lead notification FAILED to deliver.",
            metadata={"company": company},
        )

    send_async(text, on_done=_log_outcome)


if __name__ == "__main__":
    print("Probando alerta de Telegram (lead_notifier)...")
    ok = send_message(
        "🤖 <b>Test Agentic Zero</b>\n✅ lead_notifier conectado correctamente."
    )
    print(f"Mensaje enviado (modo síncrono de prueba): {ok}")
    if not ok:
        print("Revisa TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en tu .env")
