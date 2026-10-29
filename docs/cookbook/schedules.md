# Inspect and create schedules

Use a dedicated sandbox profile. Listing uses a direct Hermes Desktop HTTP endpoint and a concrete native profile name. Set `HERMES_DESKTOP_TOKEN` if required. It prints that profile's jobs and creates nothing:

```console
python examples/desktop_schedules.py --url https://DESKTOP --profile NATIVE_PROFILE
```

[Download desktop_schedules.py](https://github.com/AnasMaar/edith-hermes-sdk/blob/main/examples/desktop_schedules.py)

```python
--8<-- "examples/desktop_schedules.py"
```

Creating a job requires the control-plane URL, opaque instance/profile IDs, optional `EDITH_TOKEN`, the streaming extra, and a runtime implementing the versioned cron extension:

```console
python examples/schedule_create.py --url https://CONTROL_PLANE --instance INSTANCE --profile PROFILE --name "SDK example" --prompt "Review notes" --schedule "every 2h" --run
```

The job is created paused. The script prints its request ID before dispatch and the creation receipt afterward. If the write times out, it queries the receipt using the same ID instead of issuing a second write. An uncertain, pending, or unavailable receipt does not prove the job was absent; inspect before retrying. Delete the sandbox job through your deployment after the exercise. Enabling it later can invoke a model and incur charges.

[Download schedule_create.py](https://github.com/AnasMaar/edith-hermes-sdk/blob/main/examples/schedule_create.py)

```python
--8<-- "examples/schedule_create.py"
```
