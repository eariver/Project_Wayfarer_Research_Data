# Raw data

This directory is reserved for immutable collector output.

## Planned structure

```text
raw/
├─ polling/YYYY/MM/DD/*.jsonl
├─ rankings/YYYY/MM/DD/*.jsonl
└─ manifests/YYYY/MM/DD/*.json
```

## Rules

- Production collectors add new files only.
- Existing polling, ranking, and manifest files must not be modified, renamed, or deleted.
- One acquisition uses one unique `run_id`.
- Failed and partial acquisitions are preserved rather than removed.
- A failure is represented explicitly and is never converted to `0 players`.
- Raw files contain observations and acquisition metadata only; classification and interpretation belong elsewhere.
- Corrections are stored under `corrections/` and do not replace the original raw file.
