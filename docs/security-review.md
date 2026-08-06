# Security Reviw

## AI Findings

| ID | Severity | File / location | Finding | Evidence | Suggested next step | Confidence | Grade | Reason |
|---|---|---|---|---|---|---|---|---|
| SEC-01 | Medium | `app/models.py:60`; `app/storage.py:139` | Explicitly patching `title` to `null` can corrupt the stored task and cause server errors. | `TaskUpdate.title` permits `None`, and its validator returns `None`. Because `model_dump(exclude_unset=True)` includes explicitly supplied nulls, `model_copy(update=changes)` can place `None` into a `TaskResponse.title: str` without revalidation. Response serialization may then fail, and search later calls `task.title.lower()` at `app/storage.py:98`. No test covers `{"title": null}`. | Either reject explicit null titles or remove `title` from changes when its value is `None`. Add PATCH-null and subsequent list/search regression tests. | High | TODO | TODO |
| SEC-02 | Medium | `app/models.py:22`; `app/main.py:52`; `app/storage.py:69` | Several attacker-controlled strings and collection operations are unbounded. | Only `title` has a 200-character limit. `description`, `assignee`, `search`, and path IDs have no declared length limits. Task creation has no application-level count/rate limit, while `GET /tasks` copies, filters, searches, and returns the entire in-memory collection without pagination. This can amplify memory and CPU use if the service is exposed. | Add proportionate field/query limits, request/body-size enforcement at the serving layer, pagination or a task-count ceiling, and rate limiting if deployed beyond trusted local use. | High | TODO | TODO |
| SEC-03 | Medium | `app/main.py:13` | CORS trusts the opaque `null` origin while the API requires no authentication. | `allow_origins` includes `"null"` and all methods and headers are allowed. Sandboxed documents and locally opened files can send a `null` origin; they could therefore read and mutate this unauthenticated local API when it is running. Credentialed CORS is not enabled, but these endpoints require no credentials. | Remove `"null"` unless file-origin access is specifically required. Prefer the exact origins used by the separately hosted frontend and narrow methods/headers to those needed. | High | TODO | TODO |
| SEC-04 | Informational | `README.md:15`; `AGENTS.md:7`; `app/main.py:52` | Every caller can list, create, read, modify, and delete every task. This is documented as an intentional course-scope decision, not an accidental omission. | There is no authentication or ownership check on any route. README and AGENTS explicitly state that authentication, authorization, persistent storage, and production deployment are outside scope. | Keep the limitation prominent. Before any shared or production deployment, add authentication and object-level authorization; this requires explicit approval under the Module 5 guardrails. | High | TODO | TODO |
| SEC-05 | Low | `requirements.txt:1`; `.github/workflows/ci.yml:15` | Builds are only partially reproducible, and CI has no visible supply-chain or security checks. | Top-level Python packages are version-pinned, but transitive dependencies are neither locked nor hash-verified. GitHub Actions use major-version tags rather than commit SHAs. CI only installs dependencies and runs pytest; no dependency audit, secret scan, SAST, lint, or type check is present. This audit did not verify whether any listed version has a known vulnerability. | For a higher-assurance workflow, use a reviewed lock file with hashes, pin actions to commit SHAs, declare minimal workflow permissions, and add a dependency/security scan. | High | TODO | TODO |
| SEC-06 | Low | `Dockerfile:4`; `Dockerfile:15` | The container base is mutable and not digest-pinned. | Both stages use `python:3.11-slim`, so identical source can resolve to different base images over time. The container otherwise has a positive control: it runs as the non-root `app` user at line 26. | Pin a reviewed image digest and update it through a controlled dependency process if reproducible builds are required. Consider a health check as an operational hardening measure. | High | TODO | TODO |

## My Manual Findings

| Severity | File:Line | Finding | Suggested Fix | Reason |
|---|---|---|---|---|
|  |  |  |  |  |

## Reconciliation

### Agreement

TODO

### AI-only

TODO

### You-only

TODO

## Top 3 Unfixed Backlog

| Rank | Finding | Severity | Owner | Next Step |
|---|---|---|---|---|
| 1 | TODO | TODO | TODO | TODO |
| 2 | TODO | TODO | TODO | TODO |
| 3 | TODO | TODO | TODO | TODO |
