# Collector contract

This directory defines the machine-readable boundary between scheduled collectors and repository validation.

## Contract rules

- Each record declares `schema_version` and `record_type`.
- Production observations are written under `raw/`; examples belong under `samples/`.
- A collector run has one run manifest and one or more data files.
- JSON Lines files contain one complete JSON object per non-empty line.
- Unknown or unavailable values use explicit `null` or enumerated states; they are not guessed.
- A successful Server List Ping record must contain player counts and must not contain a failure object.
- A failed ping must not report player counts as zero.
- Ranking records preserve listed values separately from later human classification.
- Schema changes require a new semantic `schema_version`; historical files retain their original version.

## Schemas

| File | Record type |
| --- | --- |
| `server-ping-record.schema.json` | Direct Minecraft Server List Ping observation |
| `minecraft-jp-ranking-record.schema.json` | One listed server entry in a ranking snapshot |
| `run-manifest.schema.json` | Acquisition run metadata and produced-file inventory |

The initial schemas are bootstrap contracts. Collector implementation must be reviewed against sample data before production polling starts.
