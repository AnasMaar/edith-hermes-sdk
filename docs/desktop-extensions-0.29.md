# Desktop bindings 0.29.0

- `AsyncGitMutations.mutate` preserves branch creation, first-push options,
  draft state and pull-request title/body/head/base. Definite preflight failures
  produce a durable `rejected` receipt; uncertain mutations remain non-replayable.
- `AsyncGitMutations.provider` discovers the actual owning host's GitHub CLI
  account and native repository-filtered pull requests. Credentials never enter
  the response. The installed deployment must advertise `git.provider`.
- `AsyncRoomPolicy.authorize` binds native RoomLink approval behavior to an
  exact admitted room, member, installation, profile and catalog digest.
- `AsyncArtifactHistory.session` reads native session ownership and lineage for
  safe adoption of historical artifact origins into a renderer's chat registry.

These extensions are explicit versioned capabilities, separate from native
Hermes REST/RPC bindings. Unsupported deployments must report unavailability.
