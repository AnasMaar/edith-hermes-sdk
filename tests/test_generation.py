from __future__ import annotations

import json
from pathlib import Path

from edith_hermes.generated.operations import HERMES_RPC_METHODS, OPERATIONS

ROOT = Path(__file__).resolve().parents[1]


def test_all_contract_operations_are_generated() -> None:
    assert len(OPERATIONS) == 63
    assert len({operation["operation_id"] for operation in OPERATIONS}) == 63
    assert {
        operation["operation_id"]
        for operation in OPERATIONS
        if operation["namespace"] == "inference"
    } == {
        "createChatCompletion",
        "createCompletion",
    }


def test_pinned_gateway_is_complete() -> None:
    contract = json.loads(
        (ROOT / "contracts/vendor/hermes/gateway-contract.openrpc.json").read_text(encoding="utf-8")
    )
    assert len(contract["methods"]) == 219
    assert len(HERMES_RPC_METHODS) == 219
    assert set(HERMES_RPC_METHODS) == {method["name"] for method in contract["methods"]}
