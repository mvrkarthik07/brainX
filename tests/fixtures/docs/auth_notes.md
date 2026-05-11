# Auth Notes

BrainX should treat authentication notes as local-only operational knowledge.
Session tokens must never leave the device.
Refresh token handling should be explicit, auditable, and easy to inspect.

## Implementation

Use short-lived session state.
Store secrets in local configuration with careful file permissions.
Log auth failures with enough context to debug safely.
