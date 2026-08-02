# Project Wayfarer Research Data

Public raw and derived data for Minecraft server market research supporting [Project Wayfarer](https://github.com/eariver/Project_Wayfarer).

## Status

This repository is in the bootstrap stage. It defines the storage contract, validation boundary, and repository layout for future polling. It does not yet contain production polling data or an approved collector.

The governing research direction is reviewed in Project Wayfarer. This repository implements only reproducible data storage and mechanical processing.

## Responsibility boundary

| Component | Responsibility |
| --- | --- |
| Luna Max scheduled execution | Collect observations, create immutable raw files and run manifests, then commit and push them here |
| GitHub Actions | Validate schemas and mechanically derive reproducible aggregates |
| Human analysis | Decide anomaly handling, classify themes, interpret market changes, and update Project Wayfarer concepts |

Automated processing must not infer missing values, classify server themes, declare a server successful or failed, or rewrite historical raw observations.

## Data principles

- This repository remains public.
- Raw observations are append-only and immutable.
- `0 players`, acquisition failure, unknown, and not checked are distinct states.
- Every scheduled or manual acquisition has a unique `run_id`.
- Timestamps use ISO 8601 with an explicit UTC offset.
- Server and network records use stable identifiers rather than display names as keys.
- Derived data must be reproducible from raw data and versioned processing code.
- Corrections are additive records; raw files are not edited in place.
- Non-public Discord content and other authenticated community information are outside the research scope.

## Planned layout

```text
.github/workflows/       Raw validation and later aggregation workflows
collector-contract/      JSON Schemas and collector-facing contracts
config/                  Version-controlled polling and source configuration
raw/                     Immutable collector output
derived/                 Reproducible machine-generated aggregates
corrections/             Additive correction records
samples/                 Non-production example data
tools/                   Validation and aggregation programs
```

## Bootstrap scope

The first foundation change provides:

- collector contracts for server ping, minecraft.jp ranking, and run manifest records;
- sample records that are explicitly outside `raw/`;
- a Python validator;
- a GitHub Actions workflow that validates contracts, samples, and future raw data;
- directory-level rules for raw, derived, and correction data.

It intentionally does not provide:

- a Minecraft Server List Ping collector;
- minecraft.jp scraping or polling logic;
- credentials or scheduled Luna Max execution;
- production polling panel entries;
- daily, calibration, monthly, or quarterly aggregation logic.

Those require separate implementation review.

## Licensing

No repository-wide license has been selected yet. Code and data licensing will be decided separately before third-party reuse is encouraged.
