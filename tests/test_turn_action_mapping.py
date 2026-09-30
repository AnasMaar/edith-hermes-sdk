from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from edith_hermes_control_plane.auth import Identity
from edith_hermes_control_plane.engine import Problem, ProductionEngine


@pytest.mark.parametrize(
    "body,method,extra",
    [
        ({"type": "stop"}, "session.interrupt", {}),
        (
            {"type": "steer", "content": "different approach"},
            "session.steer",
            {"text": "different approach"},
        ),
        (
            {"type": "approval", "requestId": "r", "decision": "allow_once"},
            "approval.respond",
            {"request_id": "r", "choice": "once"},
        ),
        (
            {"type": "approval", "requestId": "r", "decision": "allow_session"},
            "approval.respond",
            {"request_id": "r", "choice": "session"},
        ),
        (
            {"type": "approval", "requestId": "r", "decision": "deny"},
            "approval.respond",
            {"request_id": "r", "choice": "deny"},
        ),
    ],
)
async def test_turn_actions_use_native_parameter_names(body, method, extra):
    engine = ProductionEngine.__new__(ProductionEngine)
    engine.required = AsyncMock(
        side_effect=[
            {"sessionId": "s"},
            {"id": "s", "nativeSessionId": "native-s", "instanceId": "i", "profileId": "p"},
        ]
    )
    engine._profile_name = AsyncMock(return_value="Adam")
    engine._native = AsyncMock(return_value={"result": {"accepted": True}})
    identity = Identity("tenant", "user")
    status, result = await engine.handle(
        "actOnTurn",
        {
            "instanceId": "i",
            "profileId": "p",
            "sessionId": "s",
            "turnId": "t",
            "body": body,
        },
        identity,
    )
    assert status == 202 and result == {"accepted": True}
    engine._native.assert_awaited_once_with(
        "i",
        identity,
        method,
        {
            "session_id": "native-s",
            "profile": "Adam",
            **extra,
        },
    )


async def test_turn_action_rejects_mismatched_scope_before_native_call():
    engine = ProductionEngine.__new__(ProductionEngine)
    engine.required = AsyncMock(
        side_effect=[
            {"sessionId": "other-session"},
            {"id": "s", "instanceId": "i", "profileId": "p"},
        ]
    )
    engine._native = AsyncMock()
    with pytest.raises(Problem) as failure:
        await engine.handle(
            "actOnTurn",
            {
                "instanceId": "i",
                "profileId": "p",
                "sessionId": "s",
                "turnId": "t",
                "body": {"type": "stop"},
            },
            Identity("tenant", "user"),
        )
    assert failure.value.status == 404
    engine._native.assert_not_awaited()
