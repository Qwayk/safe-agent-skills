from __future__ import annotations

import json
from typing import Any

from ..errors import SafetyError, ValidationError
from ..plans import (
    BEFORE_STATE_REFUSAL_REASON,
    build_before_state_refusal_verification_plan,
    summarize_request,
)
from ..commands._helpers import (
    find_operation,
    plan_for_operation,
    plan_from_file_for_apply,
)


def _parse_voice_settings(value: str | None) -> dict[str, Any] | None:
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid --voice-settings JSON: {exc}") from exc


def cmd_tts_synthesize(args, ctx) -> int:
    voice_id = str(getattr(args, "voice_id", "") or "").strip()
    text = str(getattr(args, "text", "") or "").strip()
    if not voice_id:
        raise ValidationError("Missing --voice-id")
    if not text:
        raise ValidationError("Missing --text")

    op = find_operation("text_to_speech")
    selector = {"kind": "tts.synthesize", "value": voice_id}
    voice_settings = _parse_voice_settings(getattr(args, "voice_settings", None))
    payload: dict[str, Any] = {"text": text}
    if getattr(args, "model_id", None):
        payload["model_id"] = args.model_id
    if voice_settings:
        payload["voice_settings"] = voice_settings
    if getattr(args, "format", None):
        payload["format"] = args.format
    request = summarize_request(op=op, params={"voice_id": voice_id}, body=payload)
    plan, plan_path = plan_for_operation(ctx=ctx, op=op, selector=selector, request=request)

    if ctx.get("plan_in"):
        applied_plan = plan_from_file_for_apply(ctx=ctx, op=op)
        if applied_plan:
            plan = applied_plan

    if not ctx.get("apply"):
        ctx["audit"].write("tts.synthesize.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    if not ctx.get("live"):
        raise SafetyError("Refused: --apply requires --live for text-to-speech")
    if not ctx.get("ack_spend_money"):
        raise SafetyError("Refused: spend-money operations require --ack-spend-money")
    ctx["audit"].write(
        "tts.synthesize.refused",
        {"reason": BEFORE_STATE_REFUSAL_REASON, "before_state": plan.get("before_state")},
    )
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": [BEFORE_STATE_REFUSAL_REASON],
            "refusal_type": "SafetyError",
            "plan": plan,
            "plan_out": plan_path,
            "verification_plan": build_before_state_refusal_verification_plan(),
        }
    )
    return 0
