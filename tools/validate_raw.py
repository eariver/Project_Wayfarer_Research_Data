#!/usr/bin/env python3
"""Validate Project Wayfarer research records and manifest references."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_FILES = {
    "server_ping": "server-ping-record.schema.json",
    "minecraft_jp_ranking": "minecraft-jp-ranking-record.schema.json",
    "run_manifest": "run-manifest.schema.json",
}


class RepositoryValidationError(Exception):
    """Raised when repository data violates a contract or invariant."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RepositoryValidationError(f"{path}: invalid JSON: {exc}") from exc


def load_validators(root: Path) -> dict[str, Draft202012Validator]:
    validators: dict[str, Draft202012Validator] = {}
    schema_root = root / "collector-contract"
    for record_type, filename in SCHEMA_FILES.items():
        schema_path = schema_root / filename
        schema = load_json(schema_path)
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # jsonschema exposes several schema error classes
            raise RepositoryValidationError(
                f"{schema_path}: invalid JSON Schema: {exc}"
            ) from exc
        validators[record_type] = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )
    return validators


def iter_json_records(path: Path) -> Iterable[tuple[int, dict[str, Any]]]:
    if path.suffix == ".jsonl":
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise RepositoryValidationError(f"{path}: cannot read file: {exc}") from exc
        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RepositoryValidationError(
                    f"{path}:{line_number}: invalid JSON: {exc}"
                ) from exc
            if not isinstance(record, dict):
                raise RepositoryValidationError(
                    f"{path}:{line_number}: each JSONL record must be an object"
                )
            yield line_number, record
        return

    value = load_json(path)
    if isinstance(value, dict):
        yield 1, value
        return
    if isinstance(value, list):
        for index, record in enumerate(value, start=1):
            if not isinstance(record, dict):
                raise RepositoryValidationError(
                    f"{path}:{index}: each array item must be an object"
                )
            yield index, record
        return
    raise RepositoryValidationError(f"{path}: JSON root must be an object or array")


def discover_data_files(root: Path, requested_paths: list[str]) -> list[Path]:
    discovered: set[Path] = set()
    for requested in requested_paths:
        candidate = root / requested
        if not candidate.exists():
            continue
        if candidate.is_file() and candidate.suffix in {".json", ".jsonl"}:
            discovered.add(candidate)
            continue
        if candidate.is_dir():
            for suffix in ("*.json", "*.jsonl"):
                discovered.update(candidate.rglob(suffix))
    return sorted(discovered)


def format_schema_errors(
    validator: Draft202012Validator,
    record: dict[str, Any],
) -> list[str]:
    messages: list[str] = []
    for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "<root>"
        messages.append(f"{location}: {error.message}")
    return messages


def validate_cross_field_invariants(
    path: Path,
    line_number: int,
    record: dict[str, Any],
) -> None:
    record_type = record.get("record_type")
    if record_type == "server_ping" and record.get("result") == "success":
        online = record.get("online_players")
        maximum = record.get("max_players")
        if isinstance(online, int) and isinstance(maximum, int) and online > maximum:
            raise RepositoryValidationError(
                f"{path}:{line_number}: online_players ({online}) exceeds max_players ({maximum})"
            )

    if record_type == "run_manifest":
        expected = record.get("expected_targets")
        attempted = record.get("attempted_targets")
        successful = record.get("successful_targets")
        failed = record.get("failed_targets")
        if all(isinstance(value, int) for value in (expected, attempted, successful, failed)):
            if attempted != successful + failed:
                raise RepositoryValidationError(
                    f"{path}:{line_number}: attempted_targets must equal successful_targets + failed_targets"
                )
            if attempted > expected:
                raise RepositoryValidationError(
                    f"{path}:{line_number}: attempted_targets must not exceed expected_targets"
                )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_records(path: Path) -> int:
    return sum(1 for _ in iter_json_records(path))


def validate_manifest_references(
    root: Path,
    manifests: list[tuple[Path, int, dict[str, Any]]],
) -> None:
    manifests_by_run: dict[str, list[Path]] = defaultdict(list)
    for manifest_path, line_number, manifest in manifests:
        run_id = manifest["run_id"]
        manifests_by_run[run_id].append(manifest_path)

        for file_entry in manifest["files"]:
            referenced_path = root / file_entry["path"]
            if not referenced_path.is_file():
                raise RepositoryValidationError(
                    f"{manifest_path}:{line_number}: referenced file does not exist: {file_entry['path']}"
                )

            actual_hash = sha256_file(referenced_path)
            if actual_hash != file_entry["sha256"]:
                raise RepositoryValidationError(
                    f"{manifest_path}:{line_number}: SHA-256 mismatch for {file_entry['path']}: "
                    f"expected {file_entry['sha256']}, got {actual_hash}"
                )

            actual_count = count_records(referenced_path)
            if actual_count != file_entry["record_count"]:
                raise RepositoryValidationError(
                    f"{manifest_path}:{line_number}: record_count mismatch for {file_entry['path']}: "
                    f"expected {file_entry['record_count']}, got {actual_count}"
                )

            for referenced_line, referenced_record in iter_json_records(referenced_path):
                if referenced_record.get("record_type") != file_entry["record_type"]:
                    raise RepositoryValidationError(
                        f"{referenced_path}:{referenced_line}: record_type does not match manifest entry"
                    )
                if referenced_record.get("run_id") != run_id:
                    raise RepositoryValidationError(
                        f"{referenced_path}:{referenced_line}: run_id does not match manifest"
                    )

    duplicates = {
        run_id: paths for run_id, paths in manifests_by_run.items() if len(paths) > 1
    }
    if duplicates:
        rendered = "; ".join(
            f"{run_id}: {', '.join(str(path) for path in paths)}"
            for run_id, paths in sorted(duplicates.items())
        )
        raise RepositoryValidationError(f"multiple manifests found for the same run_id: {rendered}")


def validate_repository(root: Path, requested_paths: list[str]) -> tuple[int, int]:
    validators = load_validators(root)
    files = discover_data_files(root, requested_paths)
    records_validated = 0
    manifests: list[tuple[Path, int, dict[str, Any]]] = []

    for path in files:
        for line_number, record in iter_json_records(path):
            record_type = record.get("record_type")
            validator = validators.get(record_type)
            if validator is None:
                raise RepositoryValidationError(
                    f"{path}:{line_number}: unknown or missing record_type: {record_type!r}"
                )

            errors = format_schema_errors(validator, record)
            if errors:
                joined = "\n  - ".join(errors)
                raise RepositoryValidationError(
                    f"{path}:{line_number}: schema validation failed:\n  - {joined}"
                )

            validate_cross_field_invariants(path, line_number, record)
            if record_type == "run_manifest":
                manifests.append((path, line_number, record))
            records_validated += 1

    validate_manifest_references(root, manifests)
    return len(files), records_validated


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root; defaults to the current directory.",
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        default=["samples", "raw"],
        help="Files or directories relative to the repository root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    try:
        file_count, record_count = validate_repository(root, args.paths)
    except RepositoryValidationError as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"validated {record_count} records across {file_count} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
