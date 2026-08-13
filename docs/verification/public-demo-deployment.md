# Public Demo Deployment Contract

This repository does not authorize a deployment by itself. Before any public Demo action, the user must provide a separate authorization record containing `REVIEWLENS_DEPLOYMENT_AUTHORIZED` and the selected platform/account scope.

The authorized Demo must run `APP_MODE=demo`, use Mock output, remain stateless, serve HTTPS, and expose no Vault/private route. After a real URL exists, verify it with:

```sh
bash scripts/verify-public-demo.sh --url "$REVIEWLENS_DEMO_URL"
```

Record only the real URL, timestamp, command result, and any failure in `AGENT_LOG.md`. Do not add a placeholder deployment URL to the README.
