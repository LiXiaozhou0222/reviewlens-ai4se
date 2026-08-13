# External Release Resume Checklist

This checklist records real outstanding evidence. It must not be marked complete until each command has actually succeeded and its result is recorded in `AGENT_LOG.md`.

## Local Tooling

1. Confirm Docker Desktop is running with Linux containers:

   ```powershell
   docker version
   docker buildx version
   ```

2. Confirm GNU Make is available:

   ```powershell
   make --version
   ```

3. Run the unified local commands:

   ```powershell
   make test
   make lint
   make build
   ```

4. Build and smoke the local image only after `make build` succeeds:

   ```powershell
   docker run --rm -p 8080:8080 -e APP_MODE=demo reviewlens:test
   ```

   Verify `/ready` reports `{"status":"ready","mode":"demo"}` and `/admin/v1/vault/status` remains unavailable.

## Remote Evidence

1. Push the approved integration branch only after the user authorizes the remote action.
2. Confirm the latest GitHub Actions and NJU GitLab `unit-test` pipelines are actually passing.
3. Create and push an authorized release tag; confirm the GHCR workflow published a real `linux/amd64` image reference and digest.
4. Run `scripts/verify-container-start.sh` against that published image in Demo and private modes.
5. Obtain separate user authorization for a public Demo deployment, then run `scripts/verify-public-demo.sh --url "$REVIEWLENS_DEMO_URL"` against the real HTTPS URL.
6. Record only real command outputs, CI URLs, image digest, and Demo URL. Do not backfill placeholders.
