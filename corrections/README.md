# Corrections

This directory is reserved for additive correction records.

A correction explains how a known acquisition or registry issue should be handled during normalization or aggregation. It does not edit or delete the original raw observation.

Each future correction record should identify:

- the affected `run_id`, file, record, or server identifier;
- the reason for the correction;
- the corrected normalized value or exclusion instruction;
- the author and timestamp;
- the evidence or review reference;
- the correction schema version.

The formal correction schema will be added with the normalization implementation.
