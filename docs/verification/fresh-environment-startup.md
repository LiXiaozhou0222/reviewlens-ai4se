# Fresh Image Startup Verification

Run this only after a real public GHCR tag has been published and Docker is available:

```sh
bash scripts/verify-container-start.sh --image "$IMAGE_REF:$RELEASE_VERSION" --mode demo
bash scripts/verify-container-start.sh --image "$IMAGE_REF:$RELEASE_VERSION" --mode private
```

The script rejects an omitted image reference before it can claim a fresh pull/run result. Record the real image reference, digest, timestamp, command output, and any failure in `AGENT_LOG.md`; do not substitute a local image or fabricate a digest.
