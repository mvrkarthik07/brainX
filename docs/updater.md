# Desktop updater (Tauri v2)

BrainX uses Tauri’s updater so installed apps can receive **signed updates**.

## Critical safety rule

Updates must update **app code only** and must **not overwrite user data**.

BrainX stores runtime state outside the app bundle (see `brain.config.paths`), so updates should not touch:

- `user.db`
- `user.faiss`
- documents
- snapshots
- local config
- feedback history
- graph state

## What “updater” does (and does not do)

- **Does**: replace the installed application bundle/binary with a newer signed version.
- **Does not**: migrate your database automatically (BrainX must do this at runtime).

This is why BrainX includes a SQLite migration system (`brain.storage.migrations`).

## Keys

Tauri updater uses a public/private keypair:

- **Public key**: safe to commit; goes into the app config.
- **Private key**: must **never** be committed; store as a secret (CI) or local-only file.

Do not commit:

- private key files (`*.key`, `*.pem`)
- signature files (`*.sig`)

`.gitignore` is configured accordingly.

## Generate keys (local)

Use the Tauri CLI to generate updater keys:

```bash
cd apps/desktop
npm run tauri signer generate
```

This prints:

- a **public key** (put in `tauri.conf.json`)
- a **private key** (store somewhere safe; never commit)

## Configure the updater

Alpha approach: host a static `latest.json` at a stable URL (for example, GitHub Releases).

The app should be configured with:

- an updater endpoint URL (points to `latest.json`)
- the public key used to verify signatures

## Release flow (high level)

1. Bump version (desktop + backend if needed)
2. Build backend sidecar for each platform
3. Build Tauri app
4. Sign artifacts
5. Upload artifacts to GitHub Release
6. Update `latest.json` to point to new artifacts and signatures
7. Test updating from an **installed** older version

## Testing updates

Updater only works when running the **installed packaged app**, not the regular `tauri dev` flow.

Recommended test:

- install `0.0.1`
- publish `0.0.2` (signed)
- confirm installed `0.0.1` updates to `0.0.2`

