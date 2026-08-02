# Luna Max Data Collection Runbook

**Repository:** `eariver/Project_Wayfarer_Research_Data`  
**Role:** Single human-readable entry point for future data-collection work  
**Status:** On hold; the 2026-08-02 expanded ranking trial is complete; no collection is currently authorized  
**Last updated:** 2026-08-02

> [!IMPORTANT]
> Luna Max must begin future work from this file. This file defines the current authorization state, work boundary, operational sequence, and stop conditions. Machine-readable field validity is defined by the JSON Schemas under `collector-contract/`. If this file and a Schema conflict, stop and report the conflict rather than guessing.

## 1. Purpose

This repository stores public, reproducible observations of Japanese public Minecraft servers for Project Wayfarer market research.

The processing chain is separated deliberately:

1. **Collector operator or Luna Max:** collect only explicitly approved observations, create immutable Raw files and one Run Manifest, validate them, and push them to this repository.
2. **GitHub Actions:** validate Raw data and generate reproducible mechanical aggregates.
3. **Human analysis / Project Wayfarer chat:** decide anomaly handling, classify themes, interpret changes, and update Project Wayfarer concepts.

Collectors and GitHub Actions must not perform market interpretation or alter Project Wayfarer concept evaluations.

## 2. Normative sources and precedence

Use the following precedence:

1. This Runbook: authorization, scope, operational sequence, and stop conditions.
2. `collector-contract/*.schema.json`: exact machine-readable fields and constraints.
3. An explicitly approved configuration under `config/`.
4. `raw/README.md`, `derived/README.md`, and `corrections/README.md`.
5. `samples/`: synthetic examples only.

`config/polling-panel.example.yml` is disabled and synthetic. It is not a production panel.

## 3. Current authorization state

### Repository state

- The repository is retained for possible reuse during a future irregular market check.
- No scheduled, recurring, monthly, quarterly, Phase A, Phase B, or Phase C collection is active.
- No automated minecraft.jp access is currently authorized.
- No direct Minecraft Server List Ping is currently authorized.
- No Luna Max schedule or production credential is currently required.
- Existing Raw and Derived files are historical records and must remain immutable.
- Collector source code, tests, Schemas, Config history, and aggregation tools are retained for reuse.
- The completed trial workflow is archived under `archive/workflows/` and is intentionally absent from `.github/workflows/`.

### Work allowed while on hold

- Reading and analyzing existing Raw or Derived data.
- Running unit tests and local validation without external collection.
- Maintaining Schemas, validators, tests, and documentation through reviewed Pull Requests.
- Preparing a proposed future one-time check without executing it.

### Work not authorized while on hold

- Accessing minecraft.jp or another source for a new collection run.
- Reusing a completed Run ID.
- Enabling an archived workflow directly.
- Creating a scheduled workflow.
- Writing new real observations under `raw/`.
- Performing direct Server List Ping against real endpoints.
- Inferring Stable IDs or classifications from names without human approval.

## 4. Completed expanded ranking trial

The one-time expanded ranking trial is complete.

```text
Trial ID: manual-expanded-rankings-2026-08-02
Run ID: 45ec07fb-f779-46e0-aea4-123dbca9243a
Started: 2026-08-02T20:48:05+09:00
Finished: 2026-08-02T20:48:13+09:00
Scope: Score ranks 1-30, Player ranks 1-20, Recent ranks 1-20
Expected / attempted / successful / failed: 70 / 70 / 70 / 0
Direct Server List Ping: not performed
```

Authoritative records:

```text
config/trials/manual-expanded-rankings-2026-08-02.json
raw/manifests/2026/08/02/2026-08-02T20-48-05+09-00_45ec07fb-f779-46e0-aea4-123dbca9243a.json
docs/source-access/minecraft-jp-2026-08-02.md
```

Relevant commits:

```text
Collector and workflow: 13ff34080fc3f4655bd4f1a9e1d9e71fc6b82f95
Raw observations:       aef22a80dfaafc723c8f07b6c00e07a0a0ce82b1
Derived aggregation:    774d4cf5c47311089abd746d73293f0194fe3341
```

The completed Config has `status: completed`. It is a historical record, not an executable authorization.

## 5. Future collection policy

Future checks are expected to be **irregular and explicitly requested**, not scheduled.

A future check requires all of the following in one reviewed change:

1. A new Config with a new Trial ID and UUID-compatible Run ID.
2. Explicit owner authorization for that exact run.
3. Exact source URLs and record range.
4. A documented source-access review current at the time of execution.
5. Bounded timeout, retry, delay, concurrency, response-size, and User-Agent rules.
6. A dry run outside `raw/`.
7. Schema, Manifest, SHA-256, record-count, and immutable-history validation.
8. A reviewed execution workflow or a reviewed manual execution procedure.
9. A completion change that archives or disables the execution path after the run.

Authorization for one run does not authorize another run, a broader scope, or recurrence.

## 6. Public-information boundary

Allowed only when explicitly authorized for a run:

- minecraft.jp public pages;
- public official websites requiring no authentication;
- public Wikis and announcements;
- public GitHub repositories;
- public social-media posts.

Excluded:

- information visible only after joining Discord;
- member-only or approval-only areas;
- authenticated non-public pages;
- data obtained by joining a game server without explicit authorization;
- bypassing access controls, robots guidance, rate limits, or source terms.

Do not store credentials, cookies, tokens, or private information.

## 7. Responsibility boundary

### Collector operator or Luna Max

When a future run is approved:

- read the approved Config;
- preserve source values without interpretation;
- distinguish successful zero-player observations from acquisition failures;
- create JSONL Raw files and one Manifest;
- validate before Git operations;
- add only new immutable files;
- report run ID, timestamps, counts, files, commit SHA, and Actions result.

Must not:

- classify themes or Primary Loops;
- declare success or failure of a server business or community;
- discard outliers without an approved mechanical rule;
- convert failures to zero players;
- guess missing values;
- edit, rename, or delete historical Raw files;
- change Project Wayfarer concepts.

### GitHub Actions

May:

- validate Schemas and cross-field invariants;
- verify Manifest ownership, hashes, and record counts;
- detect Raw modifications or deletion;
- generate deterministic Derived outputs.

Must not:

- rewrite Raw data;
- infer missing values;
- classify themes;
- decide anomaly exclusions;
- choose research conclusions.

### Human analysis

Responsible for:

- deciding whether an anomaly is usable;
- Stable ID approval;
- Server / Network and Backend / Theme separation;
- theme classification;
- interpretation and Project Wayfarer decisions.

## 8. Data contract

Use the active Schemas under `collector-contract/`:

- `server-ping-record.schema.json`
- `minecraft-jp-ranking-record.schema.json`
- `run-manifest.schema.json`

Do not add unapproved fields. Propose Schema changes before collection.

Raw paths:

```text
raw/polling/YYYY/MM/DD/*.jsonl
raw/rankings/YYYY/MM/DD/*.jsonl
raw/manifests/YYYY/MM/DD/*.json
```

Rules:

- Raw observations are append-only and immutable.
- Every observation file is referenced by exactly one Manifest.
- A Manifest does not reference another Manifest.
- Every run uses a unique Run ID and collision-resistant filename.
- Re-execution must not overwrite an existing path.
- Corrections are additive; Raw files are not edited.

Never collapse:

- successful observation with zero players;
- timeout;
- DNS failure;
- connection refusal;
- protocol failure;
- rate limiting;
- not checked;
- unknown.

For source-listed ranking records, preserve `players_online` and `players_max` independently, even when the displayed values are inconsistent. Do not clamp or infer. Successful direct Server List Ping records remain subject to their stricter integrity checks.

## 9. Stable IDs

Use only an approved Stable ID from configuration or registry.

If a listing cannot be matched:

- preserve the listing ID where the Schema permits;
- use `null` where permitted;
- report the unresolved mapping;
- do not derive a permanent identifier from a display name during collection.

## 10. One-run sequence for a future approved check

1. Synchronize with `main` without rewriting history.
2. Read this Runbook and the new approved Config.
3. Confirm the exact authorization, source, scope, and Run ID.
4. Confirm that the Run ID does not already exist.
5. Record scheduled reference time if applicable and actual start time.
6. Collect sequentially or with explicitly approved low concurrency.
7. Use bounded timeout and bounded retry.
8. Write to a temporary directory outside `raw/`.
9. Validate every record against the active Schema.
10. Compute record counts and SHA-256 hashes.
11. Create one Manifest referencing every generated observation file.
12. Validate the temporary run and existing Raw history.
13. Move only new files into final immutable Raw paths.
14. Run:

```bash
python tools/validate_raw.py --paths samples raw
```

15. Verify Git shows no historical Raw modification, rename, or deletion.
16. Commit and push without force-push.
17. Record the resulting commit SHA.
18. Confirm GitHub Actions validation and Derived generation.
19. Mark the Config completed and disable or archive the execution path.

## 11. Retry and failure policy

- Retries are finite and configured.
- A partial run records both successes and failures if the Schema can represent them.
- Do not push malformed or invalid data.
- Do not modify historical Raw data to make validation pass.
- If a source or policy preflight changes, stop before writing Raw data.
- If another run creates a conflict, rebase or merge safely; never force-push.

## 12. Source-access safeguards

The 2026-08-02 review found that minecraft.jp's public terms include general language concerning analysis or reverse engineering. This repository does not resolve its application to repeated extraction of public ranking rows.

Consequently:

- recurring automated minecraft.jp collection remains unapproved;
- each future check requires a fresh explicit decision;
- previous hashes, terms observations, and permission assumptions must not be treated as permanently valid;
- source values may be collected only under the exact approved scope.

## 13. Recurring research status

Earlier planning considered Phase A, Phase B, monthly, quarterly, and new-server tracking. These remain historical design options only.

Current decision:

- periodic trend monitoring is useful but not required;
- the repository is on hold;
- future market checks will be performed only when needed;
- any recurring program would require a new design review and explicit authorization.

## 14. Validation and retained tooling

The following remain reusable:

- JSON Schemas under `collector-contract/`;
- Raw validator and tests;
- ranking parser and collector code;
- deterministic ranking aggregation;
- completed Config and source-access record;
- archived workflow under `archive/workflows/`;
- existing Raw and Derived snapshots.

The archived workflow must not be copied back into `.github/workflows/` unchanged. A future run must use a new Config, new Run ID, current source review, and reviewed workflow.

## 15. Execution report template

```text
Task / run type:
Authorization reference:
Run ID:
Scheduled reference:
Started at:
Finished at:
Targets expected / attempted / successful / failed:
Files added:
Local validation:
Commit SHA:
Push result:
GitHub Actions result:
Known issues or follow-up:
```

Distinguish acquisition success, repository push success, and Actions success.

## 16. Change control

This file is the single human-readable entry point for future collection work.

Any change to collection scope, authorization, scheduling, file layout, source-access policy, retry policy, credentials, or operational responsibility must update this file in the same Pull Request.

Machine-readable field changes must also update the applicable Schema, samples, validator, and tests.
