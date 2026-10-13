# Desktop extension bindings, 0.26.0

`AsyncFiles.tree` now requires the owning `workspace_root` separately from the
requested directory. The host can enforce containment for nested navigation,
search and watching without treating an arbitrary requested path as a grant.

`AsyncSkillReviews` binds review, install and receipt operations to one concrete
profile. Consent identifies the reviewed quarantine bundle; installation does
not silently fetch different content after review. Receipt lookup reconciles
uncertain results without replaying installation.

`AsyncSkillDocuments` exposes a profile-owned skill's supporting tree, content
and revision-checked writes. All operations require the skill's stable identity;
paths remain relative to that skill's root.

These bindings require the explicit versioned EDITH native extension. Capability
discovery must gate their use on unextended Hermes deployments.
