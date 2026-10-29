# Define a local tool

This example requires only the installed SDK. It builds an `Agent` with a typed tool, prints its schema, and invokes it locally. It does not connect to a runtime or model.

```console
python examples/local_tool.py
```

The output contains the schema and result `2`. There are no resources to clean up. To make a tool available to a live agent, configure a suitable runtime and tool host; local invocation here does not register one.

[Download local_tool.py](https://github.com/AnasMaar/edith-hermes-sdk/blob/main/examples/local_tool.py)

```python
--8<-- "examples/local_tool.py"
```
