# Discover integrations

With the streaming extra, a running control plane, compatible native runtime, and a dedicated sandbox instance/profile, inspect sessions, background agents, groups, one plugin catalog entry, and connectors. Set `EDITH_TOKEN` if required. Replace `calendar` with a plugin name offered by your deployment:

```console
python examples/native_inventory.py --url https://CONTROL_PLANE --instance INSTANCE --profile PROFILE --plugin calendar
```

The result is JSON. The script reads the control-plane profile to resolve its native name, uses HTTP RPC for sessions, agents and groups, and the persistent gateway for catalog and connector calls. Catalog lookup is discovery, not installation or a profile-owned installed-plugin inventory. Methods may be unsupported on older runtimes. The script does not connect an account or change configuration; there is no cleanup.

[Download native_inventory.py](https://github.com/AnasMaar/edith-hermes-sdk/blob/main/examples/native_inventory.py)

```python
--8<-- "examples/native_inventory.py"
```
