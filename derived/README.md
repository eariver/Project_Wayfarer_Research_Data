# Derived data

This directory is reserved for reproducible machine-generated aggregates.

Derived outputs may include daily, calibration, monthly, quarterly, and new-server tracking datasets. Every output must identify the input period and processing version used to generate it.

## Rules

- Derived data is generated from `raw/`, additive corrections, and versioned processing code.
- GitHub Actions may write here but must never modify `raw/`.
- Human theme classification and market interpretation are not generated automatically.
- When aggregation logic changes, historical periods may be regenerated; the processing version must make that change visible.
- Human-readable reports belong in Project Wayfarer unless a report is specifically about data quality or this repository's operation.
