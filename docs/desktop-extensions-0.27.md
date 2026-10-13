# Desktop extension bindings, 0.27.0

`AsyncWorktreeHandoffs` inspects revisioned checkouts, submits one durable move,
reads its receipt and binds the existing Hermes session to the resulting
workspace. Retained recovery refs identify preserved dirty work. An uncertain
operation must be inspected, never replayed with a fresh request identity.

`AsyncRoomPeers` binds Hermes's native RoomLink capabilities, peer registration
and revocation. The versioned invite operation captures the native grant during
its reservation transaction so a lost response can be reconciled without
creating a second grant. These extensions require deployment discovery.

`AsyncLiveAudio` exposes native live status, offer negotiation, turn delegation
and hang-up with profile and session ownership. `AsyncClientWake` keeps wake
detection on its owning duplex connection and feeds bounded mono 16 kHz PCM.
It refuses execution-host microphone capture; the deployment must select client
capture explicitly. Device permission and capture belong to the desktop client.

`FileCapabilities.platform` reports the owning filesystem's platform. Clients
must not infer Windows/Unix path rules from the machine running their proxy.
