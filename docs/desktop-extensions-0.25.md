# Desktop extension bindings, 0.25.0

These bindings require the corresponding discovered `edith.desktop.v1` operations.
They do not imply that an unextended Hermes deployment provides these methods.

- `AsyncGroupAttachments`: stage files, send one durable native room event,
  project attachment metadata and read originating-host bytes. Hermes still owns
  member sessions, room execution and attachment ingestion.
- `AsyncProviderEndpoints`: inventory, scoped edits, tests and durable receipts
  around native custom endpoints. Secret values are never part of inventory.
- `AsyncScheduleMutations.snapshot/edit/edit_operation`: atomic native job
  snapshots, revision checks and receipts. Uncertain edits never authorize replay.
- `AsyncFiles.tree`: a bounded native-host snapshot with a revision; consumers
  can observe changes and search paths without inventing Desktop REST methods.

The package root now also exports the typed profile-import, group-question and
worktree-archive bindings introduced in 0.24.0.

Validation includes transport/owner contract tests. EDITH separately certifies
actual recovered UI and disposable native Hermes deployments; fixture transport
tests alone do not certify native execution or provider responses.
