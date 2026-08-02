# Luna Max Data Collection Runbook

**Repository:** `eariver/Project_Wayfarer_Research_Data`  
**Role:** Single human-readable entry point for collector implementation and scheduled data acquisition  
**Status:** Bootstrap contract; production polling is not yet authorized  
**Last updated:** 2026-08-02

> [!IMPORTANT]
> Luna Max must begin work from this file. This file defines the work boundary, collection policy, operational sequence, acceptance criteria, and stop conditions. Machine-readable field validity is defined by the JSON Schemas under `collector-contract/`. If this file and a Schema conflict, stop and report the conflict rather than guessing.

## 1. Purpose

This repository stores public, reproducible observations of Japanese public Minecraft servers for Project Wayfarer market research.

The processing chain is deliberately separated:

1. **Luna Max:** collect observations, create immutable Raw files and a Run Manifest, validate them locally, then commit and push them to this repository.
2. **GitHub Actions:** validate Raw data and generate reproducible mechanical aggregates.
3. **Human analysis / Project Wayfarer chat:** decide anomaly handling, classify server themes, interpret trends, select Peak Windows, and update Project Wayfarer concepts.

Luna Max and GitHub Actions must not perform market interpretation or change Project Wayfarer concept evaluations.

## 2. Normative sources and precedence

Use the following precedence when implementing or operating the collector:

1. This Runbook: task scope, operational sequence, safety rules, and stop conditions.
2. `collector-contract/*.schema.json`: exact machine-readable record fields and constraints.
3. Approved production files under `config/`: active targets, sources, phase, and schedule.
4. `raw/README.md`, `derived/README.md`, and `corrections/README.md`: directory-specific rules.
5. `samples/`: synthetic examples only; never treat sample endpoints or values as production configuration.

`config/polling-panel.example.yml` is intentionally disabled and synthetic. It is not an approved production panel.

## 3. Current authorization state

The repository currently authorizes only foundation and implementation work.

### Authorized

- Implementing and testing a collector against the existing Schemas.
- Implementing local preflight validation.
- Implementing GitHub Actions for mechanical validation and aggregation through reviewed Pull Requests.
- Running synthetic, fixture-based, or explicitly approved dry runs outside `raw/`.
- Preparing a production polling panel for review.

### Not yet authorized

- Production polling of real servers.
- Automated access to minecraft.jp.
- Scheduled Luna Max execution using production credentials.
- Writing real observations under `raw/`.
- Selecting a Phase A start date.
- Selecting permanent monthly or quarterly polling times before Phase B calibration.

Production collection may begin only when all stop conditions in Section 16 are cleared.

## 4. Research phases

### Phase A: Summer-holiday reference observation

Run 14 days of continuous polling after the collector, production panel, credentials, and repository workflow are approved.

Purpose:

- verify collector, Schema, Manifest, push, and Actions behavior;
- obtain a provisional weekday/time curve during the summer holiday period;
- measure possible daytime population increase;
- provide comparison data for Phase B.

Phase A must not be used alone to select the permanent market Peak Window.

### Phase B: Normal-period Peak calibration

Candidate period:

```text
2026-10-13T00:00:00+09:00
through
2026-10-25T23:59:59+09:00
```

This period may be moved if a major Minecraft release, a large server event, a collector failure, or another material disturbance overlaps it. Record the reason for any change.

Phase B is used to derive candidates for:

- weekday Peak Window;
- Saturday Peak Window;
- Sunday Peak Window;
- Primary Snapshot day and time;
- Secondary Snapshot day and time;
- recurring monthly and quarterly collection times.

The final choice is made by human analysis, not by Luna Max or GitHub Actions.

### Phase C: Recurring research

After Phase B:

- **Monthly:** lightweight observations around the approved Primary and Secondary Snapshot windows.
- **Quarterly:** seven days of hourly polling, a full listing snapshot, ranking snapshots, and public-site review.
- **New-server tracking:** T0, T1, T3, and T6 months.

## 5. Observation scope

### 5.1 Fixed polling panel

At the start of each phase, create a panel by combining:

- top 30 by minecraft.jp Score;
- top 20 by displayed Player count;
- top 20 newest listings;
- up to 10 additional servers related to Project Wayfarer candidate themes.

Deduplicate by approved stable Server or Network ID. The expected panel size is approximately 40 to 60 Networks.

Keep the panel fixed during a phase. Do not remove a server because it becomes unreachable or closes; record the state change. Add newly interesting servers at the next phase boundary unless an explicit instruction authorizes an exception.

### 5.2 Full listing snapshot

Capture all obtainable minecraft.jp listing values at:

- phase start;
- phase end;
- each quarterly research cycle.

Do not assume all listed servers should receive hourly direct pings.

### 5.3 Server and backend separation

Ranking, Score, votes, address, and direct availability belong to the Server or Network level.

Game Loop and theme classification belong to Backend or Theme records and are not Luna Max collection responsibilities.

```text
Server / Network
└─ Backend / Theme
```

## 6. Calibration polling schedule

Use JST (`Asia/Tokyo`) scheduling and store ISO 8601 timestamps with an explicit UTC offset.

| Data | Frequency | Planned timing |
| --- | --- | --- |
| Fixed Panel Server List Ping | Hourly | minute 07 JST |
| minecraft.jp Player ranking | Every 6 hours | 00:17, 06:17, 12:17, 18:17 JST |
| Score, votes, availability | Daily | approved daily time; not yet fixed |
| Full listing snapshot | Phase boundary | phase start and phase end |
| Public official-site review | Quarterly | human-led detailed research |

A delayed start is not automatically a failed run. Preserve the original `scheduled_at` and record actual `started_at` and `finished_at`.

## 7. Public-information boundary

Allowed sources:

- minecraft.jp;
- public official websites that require no authentication;
- public Wikis;
- public announcements;
- public GitHub repositories;
- public social-media posts.

Excluded sources:

- information visible only after joining Discord;
- member-only channels;
- approval-only community areas;
- authenticated non-public pages;
- information obtained by joining a game server without explicit research authorization.

Publicly displayed Discord member counts may be preserved as auxiliary listed values if a future Schema supports them, but they are not a primary community-size metric.

## 8. Luna Max responsibilities

### Required

- read the approved source and panel configuration;
- perform direct Minecraft Server List Ping for approved endpoints;
- acquire approved ranking or listing snapshots at the approved frequency;
- preserve source values without interpretation;
- create JSONL Raw files and one Run Manifest per acquisition;
- distinguish success, partial success, and failure;
- run local validation before Git operations;
- add only new immutable Raw files;
- commit and push to this public repository;
- provide a concise execution result containing the run ID, scheduled time, actual time, record counts, failures, commit SHA, and Actions status when available.

### Prohibited

- classifying themes or Primary Loops;
- declaring a server commercially or operationally successful or failed;
- discarding an outlier without an approved mechanical rule;
- converting collection failure to `0 players`;
- guessing missing values;
- editing, renaming, or deleting historical Raw files;
- changing Project Wayfarer concepts;
- storing credentials, tokens, cookies, or private information in the repository;
- bypassing robots, rate limits, access controls, or source terms;
- using the synthetic example panel as production configuration.

## 9. Raw data contract

### 9.1 Schemas

Use the current Schemas under `collector-contract/`:

- `server-ping-record.schema.json`
- `minecraft-jp-ranking-record.schema.json`
- `run-manifest.schema.json`

Do not add fields that are absent from the active Schema. Propose a Schema change through a Pull Request before collecting the new field.

### 9.2 Raw paths

Production files use:

```text
raw/polling/YYYY/MM/DD/*.jsonl
raw/rankings/YYYY/MM/DD/*.jsonl
raw/manifests/YYYY/MM/DD/*.json
```

Every production observation file must be referenced by exactly one Manifest. A Manifest must not reference another Manifest.

### 9.3 Required distinctions

Never collapse these states:

- successful observation with zero online players;
- timeout;
- DNS failure;
- connection refused;
- protocol failure;
- rate limiting;
- not checked;
- unknown.

Use the Schema-defined values. If the Schema cannot represent an observed condition, stop the affected acquisition and propose a contract change.

### 9.4 Stable IDs

Use the approved stable ID from production configuration or registry. Do not derive a new permanent ID from a display name during a scheduled run.

If a listing cannot be matched to an approved stable ID, preserve the listing ID where the Schema allows it, use `null` only where permitted, and report the unresolved mapping for human review.

## 10. File naming

Use collision-resistant, sortable names containing the scheduled timestamp and Run ID.

Recommended pattern:

```text
raw/polling/2026/08/03/2026-08-03T19-07-00+09-00_<run-id>.jsonl
raw/rankings/2026/08/03/score_2026-08-03T20-17-00+09-00_<run-id>.jsonl
raw/manifests/2026/08/03/2026-08-03T19-07-00+09-00_<run-id>.json
```

Use filename-safe timestamp punctuation consistently. Never reuse a filename, even for a retry of the same scheduled time.

## 11. One-run operational sequence

For every scheduled or manual acquisition:

1. Synchronize the local checkout with `main` without rewriting remote history.
2. Read the approved production configuration.
3. Confirm the requested phase, run type, source, and scheduled time.
4. Generate a new UUID-compatible `run_id`.
5. Record `scheduled_at` and actual `started_at`.
6. Collect approved targets using bounded timeout, bounded retry, and low concurrency.
7. Preserve every target result, including failures.
8. Write output to a temporary working directory outside `raw/`.
9. Validate each record against the active Schema.
10. Compute record counts and SHA-256 hashes.
11. Create one Manifest referencing every data file produced by the run.
12. Run repository validation against the temporary run and all existing Raw data.
13. Move or write the final files to their new immutable `raw/` paths.
14. Run:

```bash
python tools/validate_raw.py --paths samples raw
```

15. Verify Git shows only expected newly added Raw files. Existing Raw modifications, renames, and deletions are forbidden.
16. Commit with a deterministic message, for example:

```text
data(polling): collect 2026-08-03T19:07+09:00
```

17. Pull or fetch/rebase safely if another acquisition was pushed concurrently. Do not force-push.
18. Push to `main` only after local validation passes and the approved repository policy allows direct collector pushes.
19. Record the resulting commit SHA.
20. Check the validation workflow when possible and report its result.

## 12. Retry and failure policy

### Acquisition retry

- Retries must be bounded and configured, not infinite.
- Preserve only the final target result in the primary Raw record unless a future Schema explicitly supports per-attempt records.
- Record the acquisition timing honestly; do not rewrite timestamps to the expected schedule.

### Partial runs

A partial run is valid when some targets succeed and others fail. Generate Raw records for all attempted targets and set the Manifest status and counts consistently.

### Total failure

If the collector can initialize and represent the failure safely, create a failure Manifest with the appropriate counts and notes. If no valid Manifest can be produced, do not write malformed Raw data; report the operational failure separately.

### Validation failure

- Do not push invalid data.
- Do not edit existing Raw files to make validation pass.
- Preserve local diagnostics and report the exact Schema or invariant failure.
- Propose a code, configuration, or Schema fix through a Pull Request.

### Push conflict

- Fetch and rebase or merge without modifying existing Raw files.
- Unique Run IDs and filenames must allow concurrent runs to coexist.
- Never use force push.

## 13. Git and credential rules

- Luna Max requires write access only to `eariver/Project_Wayfarer_Research_Data`.
- Luna Max does not require write access to `eariver/Project_Wayfarer`.
- Use a repository-scoped GitHub App or fine-grained token with minimum necessary permissions.
- Never print credentials in logs.
- Never commit `.env`, local secrets, tokens, cookies, SSH keys, or credential files.
- Collector commits must not modify `collector-contract/`, `tools/`, `.github/`, `config/`, `derived/`, or Project documentation during a scheduled data run.
- Code, Schema, configuration, and workflow changes require a reviewed Pull Request.

## 14. GitHub Actions boundary

GitHub Actions may:

- validate Schemas and cross-field invariants;
- verify Manifest ownership, SHA-256, and record counts;
- detect Raw modifications or deletions;
- normalize mechanically;
- generate daily, calibration, monthly, quarterly, and new-server tracking aggregates;
- commit reproducible Derived outputs if the reviewed workflow explicitly permits it.

GitHub Actions must not:

- rewrite Raw data;
- infer missing values;
- classify themes;
- decide which anomalies to discard;
- choose the final Peak Window;
- change Project Wayfarer evaluations.

## 15. Collector implementation deliverables

A collector implementation Pull Request must include:

- collector source code and pinned or bounded dependencies;
- production-safe configuration parsing;
- explicit timeout, retry, concurrency, and user-agent behavior where applicable;
- Server List Ping implementation tests;
- ranking/listing parser fixtures and tests if minecraft.jp acquisition is implemented;
- Manifest generation tests;
- tests for `0 players` versus acquisition failure;
- tests for partial and total failure;
- tests proving no historical Raw file is modified;
- dry-run mode that never writes under `raw/` and never pushes;
- clear local execution commands;
- security notes for credentials;
- an updated section in this Runbook if operational behavior changes.

The implementation must pass the existing validation workflow and any new collector tests.

## 16. Production start stop conditions

Do not begin real collection until every item below is satisfied:

- [ ] Collector implementation is reviewed and merged.
- [ ] minecraft.jp terms, robots guidance, rate limits, and acceptable request frequency are checked and documented.
- [ ] Direct Server List Ping timeout, retry, and concurrency limits are approved.
- [ ] Stable ID rules and production registry are approved.
- [ ] Production polling panel is reviewed, enabled, and committed under `config/`.
- [ ] Phase and exact start/end timestamps are approved.
- [ ] Repository-scoped credentials are configured outside Git.
- [ ] Dry run succeeds without writing production Raw data.
- [ ] Synthetic or staging end-to-end run succeeds through GitHub Actions.
- [ ] Direct collector push policy and branch protection are compatible.
- [ ] Human owner explicitly authorizes production start.

If any item is incomplete, continue only with implementation, tests, fixtures, or dry-run work.

## 17. Calibration aggregation expectations

GitHub Actions should eventually derive, without interpreting:

- total Fixed Panel online players by hour;
- responding Network count;
- Network-level average, median, and maximum;
- market median and 75th/90th percentile;
- top-five Network concentration;
- weekday, Saturday, and Sunday hourly medians;
- candidate Peak Windows where consecutive values are at least 95% of the category maximum;
- sensitivity results excluding the largest Networks;
- Phase A versus Phase B comparison.

Actions output candidates only. Human analysis confirms the final Primary and Secondary Snapshot windows.

## 18. Monthly, quarterly, and new-server expectations

### Monthly

After Peak calibration, collect approved Primary and Secondary windows at Peak minus one hour, Peak, and Peak plus one hour.

Track mechanically:

- Player count;
- ranking;
- Score;
- votes;
- availability;
- version;
- new, missing, or unreachable Networks.

### Quarterly

- seven days of hourly Fixed Panel polling;
- full listing snapshot;
- Score, Player, and Recent ranking snapshots;
- machine aggregation;
- human review of public official sites and theme classifications.

### New-server tracking

Track at:

```text
T0: first observation
T1: one month
T3: three months
T6: six months
```

Six months is the standard endpoint. Luna Max preserves the observations; human analysis decides what they imply about persistence or popularity.

## 19. Execution report template

After an implementation task or scheduled run, report:

```text
Task / run type:
Phase:
Run ID:
Scheduled at:
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

Do not describe a run as successful when validation or push failed. Distinguish acquisition success, repository push success, and Actions validation success.

## 20. Change control

This file is the single human-readable entry point for Luna Max collection work. Any approved change to collection scope, scheduling, file layout, credentials, retry policy, phase timing, or operational responsibilities must update this file in the same Pull Request.

Machine-readable field changes must also update the applicable Schema, samples, validator, and tests.
