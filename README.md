# OrigoID SDK Config

Fern-based SDK generation pipeline for the [OrigoID API](https://docs.origoid.com).

## What this repo does

Reads `openapi.json` (sourced from `mintlify-poc/openapi.json`), generates SDKs
in 3 languages, and publishes them to public registries:

| Language   | Package                            | Install                              |
| ---------- | ---------------------------------- | ------------------------------------ |
| TypeScript | `@origoid/sdk` on npm              | `npm install @origoid/sdk`           |
| Python     | `origoid` on PyPI                  | `pip install origoid`                |
| Go         | `github.com/origoid/sdk-go`        | `go get github.com/origoid/sdk-go`   |

## Layout

```
fern/
  fern.config.json     # Fern org config
  generators.yml       # generator + publish config (2 groups: local, publish)
  openapi/openapi.json # synced copy of the spec (without x-codeSamples)
scripts/
  sync-openapi.py      # copy mintlify-poc/openapi.json + strip x-codeSamples
sdks/                  # local clones of origoid/sdk-{node,python,go} (gitignored)
```

## Local generation (no publish)

```bash
python3 scripts/sync-openapi.py
fern generate --group local --force
```

Outputs go to `sdks/{node,python,go}/` for inspection.

## Release a new version

1. Update the source spec in the `mintlify-poc` repo and push it so
   `docs.origoid.com/openapi.json` reflects the change.

2. Sync + regenerate locally and skim the diff:
   ```bash
   python3 scripts/sync-openapi.py
   fern generate --group local --force
   ```

3. Decide the version (semver). Initial: `0.1.0`. Patch fixes: `0.1.1`.
   Breaking changes before 1.0: bump minor (`0.2.0`).

4. Push the generated source to `origoid/sdk-{node,python,go}` and tag:
   ```bash
   fern generate --group publish --version 0.2.0 --no-prompt
   ```

   This pushes generated code to each per-language repo via the Fern GitHub
   App. It does **not** publish to npm/PyPI directly — that's done by the
   GitHub Actions workflow in each repo when a tag is created.

5. Tag each repo to trigger the publish workflow:
   ```bash
   gh release create v0.2.0 -R origoid/sdk-node --title v0.2.0 --notes "..."
   gh release create v0.2.0 -R origoid/sdk-python --title v0.2.0 --notes "..."
   gh release create v0.2.0 -R origoid/sdk-go --title v0.2.0 --notes "..."
   ```

   GitHub Actions then runs `npm publish` / `poetry publish` automatically.
   Go modules require no registry — the tag alone makes the version available.

## Secrets required

Set per repo (already done as of v0.1.0):

| Repo               | Secret           | Source                              |
| ------------------ | ---------------- | ----------------------------------- |
| `origoid/sdk-node` | `NPM_TOKEN`      | npm Automation/Granular token       |
| `origoid/sdk-python` | `PYPI_USERNAME` | literal `__token__`                 |
| `origoid/sdk-python` | `PYPI_PASSWORD` | PyPI API token (`pypi-...`)         |
| `origoid/sdk-go`   | none             | Tag alone publishes the Go module   |

Rotation: NPM_TOKEN expires 2026-08-24. PyPI token has no expiration.

## Known issues

- `fern-typescript-node-sdk` crashes on `x-codeSamples`. `sync-openapi.py`
  strips them before generation. The Mintlify docs keep them — only the
  Fern copy is stripped.
- Email endpoint 200 schema uses plain `$ref: Envelope` (no `allOf` typed
  data) to avoid `EnvelopeStatus` duplicate-declaration in the SDK output.
  Data shape stays documented via response examples.
