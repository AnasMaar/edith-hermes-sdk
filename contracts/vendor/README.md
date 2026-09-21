# Vendored upstream contracts

These snapshots make SDK generation reproducible and are not edited locally.

| Source | Pin | SHA-256 |
| --- | --- | --- |
| `hermes/gateway-contract.openrpc.json` | Hermes Agent commit `5470f260cac7bafc7b98676dfba1c12fcddc3234` | `00de4e14314d18909d36d73976552b8c53dc5106a34356d7cf2159c8177449e2` |
| `nous/inference.openapi.json` | Snapshot retrieved 2026-09-21 | `645775176ce197be1cd63943dd41198ed4c3eec272e334e88c7bb809e8ccd6ac` |

Update a snapshot deliberately, update its checksum and source metadata, regenerate the SDK, and
review the generated diff before committing.

