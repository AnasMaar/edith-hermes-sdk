# Message a bot or group

These operations require a running control plane, streaming extra, compatible native runtime and dedicated sandbox instance/profile. Set `EDITH_TOKEN` if required. Both can cause model inference and charges; `--run` explicitly opts in.

Send one message to the selected profile's Bot Chat:

```console
python examples/bot_message.py --url https://CONTROL_PLANE --instance INSTANCE --profile PROFILE --message "Say hello" --run
```

The native `bot_relay.deliver` call blocks for a one-turn reply, printed as JSON. The message may remain in Bot Chat; remove it through the deployment if supported.

[Download bot_message.py](https://github.com/AnasMaar/edith-hermes-sdk/blob/main/examples/bot_message.py)

```python
--8<-- "examples/bot_message.py"
```

Stage a local test file and send it to an existing sandbox room using the group attachment extension:

```console
python examples/group_attachment.py --url https://CONTROL_PLANE --instance INSTANCE --profile PROFILE --room ROOM --file ./note.txt --message "Read this" --run
```

The script prints the staged attachment, event ID, and send result. The room message and staged attachment can persist; remove them through your deployment if supported. A timeout can leave a write's outcome uncertain, so inspect the room before retrying.

[Download group_attachment.py](https://github.com/AnasMaar/edith-hermes-sdk/blob/main/examples/group_attachment.py)

```python
--8<-- "examples/group_attachment.py"
```
