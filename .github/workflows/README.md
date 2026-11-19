# GitHub Actions collection

The CI for this repository. It is one of three interchangeable collections
maintained in the [`claude-marketplace`](https://github.com/nerdynick/claude-marketplace)
template — GitHub Actions, Forgejo Actions, and GitLab CI. Only the GitHub one
is carried here, because this repository is hosted on GitHub; pull the others
from the template if that ever changes.

Every collection runs the **same Makefile targets**, so the checks never drift
apart from each other or from `make validate` on a laptop. Variable and secret
names are identical across all three.

## Workflows here

| File | Trigger | Does |
|---|---|---|
| `validate.yml` | `workflow_call`, `workflow_dispatch` | The whole check suite. Called by the other two rather than duplicated |
| `pull-request.yml` | `pull_request` | Validation only — nothing is packaged or published from a branch |
| `release.yml` | `push` to `main` | Validate, package, publish `v<marketplace version>` |

GitHub supports reusable workflows, so `validate.yml` is called by both. The
Forgejo collection inlines the same steps instead, because reusable-workflow
support varies by Forgejo version.

## What runs

In order, because a broken checker makes everything after it meaningless:

1. `make test` — unit tests for the validation scripts themselves
2. `make validate-manifests` — `claude plugin validate --strict`
3. `make validate-coverage` — every package registered, every source resolvable
4. `make validate-skills` — SKILL.md frontmatter, description length, line count, naming
5. `make validate-agent-docs` — `AGENTS.md` still mirrors `CLAUDE.md`

Steps 2–5 are the same checks `scripts/hooks/pre-commit` runs locally. The hook
is the fast mirror and can be bypassed with `--no-verify`; this is the backstop
that cannot.

## Variables

Set as workflow `env:` blocks. Change them there, or override per-repository
under **Settings → Secrets and variables → Actions → Variables**.

| Variable | Default | Used by | Purpose |
|---|---|---|---|
| `NODE_VERSION` | `22` | validate, release | Node used to install the Claude Code CLI |
| `PYTHON_VERSION` | `3.12` | validate, release | Python for the validation scripts and unit tests |
| `CLAUDE_CLI_PACKAGE` | `@anthropic-ai/claude-code` | validate | npm package providing `claude plugin validate` |
| `DIST_DIR` | `dist` | release | Where `make package-all` writes archives |
| `RELEASE_BRANCH` | `main` | release | Branch a release is cut from. On GitHub this is the `on: push: branches:` list |

## Secrets

| Secret | Required | Purpose |
|---|---|---|
| `RELEASE_TOKEN` | **No** | Token used to create the release. Leave it unset: the built-in `github.token` can already create releases in its own repository. Set it only to publish somewhere the job token cannot reach |

No secret is needed for validation. `claude plugin validate` runs entirely
locally — no API key, no login, no network call to Anthropic.

## Permissions

`release.yml` requests `contents: write` on its publish job only; everything
else runs read-only. If your organization defaults workflow permissions to
read-only, that per-job grant is what lets the release be created.

## Releasing

The tag is the gate. `release.yml` publishes `v<version>` where `<version>` is
the root `version` in `.claude-plugin/marketplace.json`. If that tag already
exists the run is a clean no-op, so **a release is cut exactly when that
version is bumped** — ordinary pushes to `main` publish nothing.
