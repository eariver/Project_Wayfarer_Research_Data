# Project Wayfarer Research Data

Public raw and derived data for Minecraft server market research supporting [Project Wayfarer](https://github.com/eariver/Project_Wayfarer).

## Luna Max entry point

Luna Max must start any future collector or data-acquisition work from:

- [`LUNA_MAX_DATA_COLLECTION_RUNBOOK.md`](LUNA_MAX_DATA_COLLECTION_RUNBOOK.md)

The Runbook is the single human-readable work entry point. Machine-readable record validity remains defined by the JSON Schemas under `collector-contract/`.

## Status

**On hold.** The one-time expanded minecraft.jp ranking trial completed successfully on 2026-08-02.

- Score ranking: 30 records
- Player ranking: 20 records
- Recent ranking: 20 records
- Total: 70 successful records, 0 failures
- Run ID: `45ec07fb-f779-46e0-aea4-123dbca9243a`

No scheduled or recurring collection is active or authorized. Future checks are expected to be irregular and require a new explicit authorization, Config, Run ID, source review, and reviewed execution path.

The completed execution workflow is archived under `archive/workflows/` and cannot run from that location. Existing Raw and Derived data, Schemas, Collector code, tests, and aggregation tools remain available for reuse.

## Responsibility boundary

| Component | Responsibility |
| --- | --- |
| Collector operator or Luna Max | For an explicitly approved run, collect observations, create immutable Raw files and one Manifest, validate, then commit and push |
| GitHub Actions | Validate Schemas and mechanically derive reproducible aggregates |
| Human analysis | Decide anomaly handling, Stable IDs, theme classification, market interpretation, and Project Wayfarer changes |

Automated processing must not infer missing values, classify themes, declare a server successful or failed, or rewrite historical Raw observations.

## Data principles

- This repository remains public.
- Raw observations are append-only and immutable.
- `0 players`, acquisition failure, unknown, and not checked are distinct states.
- Every acquisition has a unique `run_id`.
- Timestamps use ISO 8601 with an explicit UTC offset.
- Stable identifiers require human-approved configuration or registry entries.
- Derived data must be reproducible from Raw data and versioned processing code.
- Corrections are additive records; Raw files are not edited in place.
- Non-public Discord content and other authenticated community information are outside the research scope.
- A completed Trial Config is a historical record and does not authorize reuse.

## Repository layout

```text
.github/workflows/       Active validation and aggregation workflows only
archive/workflows/       Inactive completed workflow references
collector-contract/      JSON Schemas and collector-facing contracts
config/                  Version-controlled source and Trial configuration
raw/                     Immutable collector output
derived/                 Reproducible machine-generated aggregates
corrections/             Additive correction records
samples/                 Non-production example data
tools/                   Validation, collection, and aggregation programs
tests/                   Validator and Collector tests
docs/                    Source-access and research records
```

## Completed Trial records

```text
config/trials/manual-expanded-rankings-2026-08-02.json
raw/manifests/2026/08/02/2026-08-02T20-48-05+09-00_45ec07fb-f779-46e0-aea4-123dbca9243a.json
docs/source-access/minecraft-jp-2026-08-02.md
derived/ranking-snapshots/2026/08/02/
```

Relevant commits:

```text
Collector and workflow: 13ff34080fc3f4655bd4f1a9e1d9e71fc6b82f95
Raw observations:       aef22a80dfaafc723c8f07b6c00e07a0a0ce82b1
Derived aggregation:    774d4cf5c47311089abd746d73293f0194fe3341
```

## Licensing

No repository-wide license has been selected yet. Code and data licensing will be decided separately before third-party reuse is encouraged.
