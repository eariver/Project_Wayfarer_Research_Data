#!/usr/bin/env python3
"""Collect one approved minecraft.jp ranking trial into immutable Raw files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from jsonschema import Draft202012Validator, FormatChecker

JST = timezone(timedelta(hours=9))
RANKING_SCHEMA = "collector-contract/minecraft-jp-ranking-record.schema.json"
MANIFEST_SCHEMA = "collector-contract/run-manifest.schema.json"


class CollectionError(RuntimeError):
    """Raised when an approved collection cannot be completed safely."""


def canonical_json_line(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def preflight_hash(body: bytes, specification: dict[str, Any]) -> str:
    mode = specification.get("hash_mode", "raw")
    if mode == "raw":
        return sha256_bytes(body)
    if mode == "text_selector":
        selector = specification.get("selector")
        if not isinstance(selector, str) or not selector:
            raise CollectionError("text_selector preflight requires a selector")
        soup = BeautifulSoup(body, "html.parser")
        node = soup.select_one(selector)
        if node is None:
            raise CollectionError(f"preflight selector was not found: {selector}")
        normalized = "\n".join(
            line.strip()
            for line in node.get_text("\n").splitlines()
            if line.strip()
        )
        return sha256_bytes(normalized.encode("utf-8"))
    raise CollectionError(f"unsupported preflight hash mode: {mode}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_integer(text: str) -> int:
    return int(text.replace(",", "").strip())


def parse_optional_float(text: str) -> float | None:
    normalized = text.replace(",", "").strip()
    return float(normalized) if normalized else None


def unique_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def parse_ranking_html(
    html: bytes,
    ranking_type: str,
    captured_at: str,
    run_id: str,
    collector: dict[str, str],
) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    tbody = soup.select_one("table.table-servers tbody")
    if tbody is None:
        raise CollectionError("ranking table body was not found")

    rows = list(tbody.find_all("tr", recursive=False))
    records: list[dict[str, Any]] = []
    index = 0
    while index < len(rows):
        info_row = rows[index]
        if "row-info" not in set(info_row.get("class") or []):
            index += 1
            continue

        tags_row = None
        if index + 1 < len(rows) and "row-tags" in set(rows[index + 1].get("class") or []):
            tags_row = rows[index + 1]

        rank_cell = info_row.select_one("td.rank")
        name_cell = info_row.select_one("td.name")
        players_cell = info_row.select_one("td.players")
        score_cell = info_row.select_one("td.score")
        vote_cell = info_row.select_one("td.vote")
        uptime_cell = info_row.select_one("td.uptime")
        if None in (rank_cell, name_cell, players_cell, score_cell, vote_cell, uptime_cell):
            raise CollectionError("ranking row is missing a required cell")

        rank_match = re.search(r"(\d+)", rank_cell.get_text(" ", strip=True))
        if rank_match is None:
            raise CollectionError("ranking row has no numeric rank")
        rank = int(rank_match.group(1))

        listing_link = name_cell.find("a", href=True)
        if listing_link is None or not listing_link["href"].startswith("/servers/"):
            raise CollectionError(f"rank {rank}: listing link is missing or unexpected")
        href = listing_link["href"]
        listing_id = href.removeprefix("/servers/")
        if not listing_id:
            raise CollectionError(f"rank {rank}: empty listing ID")

        version_node = name_cell.select_one("span.label")
        listed_version = version_node.get_text(" ", strip=True) if version_node else None
        address_cell = info_row.select_one("td.address")
        listed_address = address_cell.get_text(" ", strip=True) if address_cell else None
        if not listed_address:
            listed_address = None

        players_match = re.search(
            r"([\d,]+)\s*/\s*([\d,]+)",
            players_cell.get_text(" ", strip=True),
        )
        if players_match is None:
            raise CollectionError(f"rank {rank}: player count is not parseable")
        players_online = parse_integer(players_match.group(1))
        players_max = parse_integer(players_match.group(2))

        uptime_match = re.search(r"(\d+(?:\.\d+)?)\s*%", uptime_cell.get_text(" ", strip=True))
        availability_ratio = float(uptime_match.group(1)) / 100 if uptime_match else None

        tags: list[str] = []
        if tags_row is not None:
            tags = unique_preserving_order(
                [
                    node.get_text(" ", strip=True)
                    for node in tags_row.select("td.tags span.tags-collapse span.label")
                    if node.get_text(" ", strip=True)
                ]
            )

        records.append(
            {
                "schema_version": "1.0.0",
                "record_type": "minecraft_jp_ranking",
                "run_id": run_id,
                "captured_at": captured_at,
                "ranking_type": ranking_type,
                "rank": rank,
                "server_id": None,
                "listing_id": listing_id,
                "listing_url": urljoin("https://minecraft.jp", href),
                "display_name": listing_link.get_text(" ", strip=True),
                "listed_address": listed_address,
                "listed_version": listed_version,
                "score": parse_optional_float(score_cell.get_text(" ", strip=True)),
                "players_online": players_online,
                "players_max": players_max,
                "votes_30d": parse_integer(vote_cell.get_text(" ", strip=True)),
                "availability_ratio": availability_ratio,
                "tags": tags,
                "source": "minecraft.jp",
                "collector": collector,
            }
        )
        index += 2 if tags_row is not None else 1

    return records


@dataclass
class BoundedFetcher:
    user_agent: str
    timeout_seconds: int
    max_response_bytes: int
    delay_seconds: float
    retries: int
    last_request_at: float | None = None

    def _wait(self) -> None:
        if self.last_request_at is None:
            return
        remaining = self.delay_seconds - (time.monotonic() - self.last_request_at)
        if remaining > 0:
            time.sleep(remaining)

    def fetch(
        self,
        url: str,
        accept: str = "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.1",
    ) -> bytes:
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            self._wait()
            self.last_request_at = time.monotonic()
            request = urllib.request.Request(
                url,
                headers={"User-Agent": self.user_agent, "Accept": accept},
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    body = response.read(self.max_response_bytes + 1)
                    if len(body) > self.max_response_bytes:
                        raise CollectionError(
                            f"response exceeds {self.max_response_bytes} bytes: {url}"
                        )
                    if response.status != 200:
                        raise CollectionError(f"unexpected HTTP status {response.status}: {url}")
                    return body
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, CollectionError) as error:
                last_error = error
                if attempt >= self.retries:
                    break
        raise CollectionError(f"failed to fetch {url}: {last_error}")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CollectionError(f"JSON root must be an object: {path}")
    return value


def load_validator(path: Path) -> Draft202012Validator:
    schema = load_json(path)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate_object(
    validator: Draft202012Validator,
    value: dict[str, Any],
    label: str,
) -> None:
    errors = sorted(validator.iter_errors(value), key=lambda error: list(error.path))
    if errors:
        rendered = "; ".join(
            f"{'.'.join(map(str, error.path)) or '<root>'}: {error.message}"
            for error in errors
        )
        raise CollectionError(f"{label} failed Schema validation: {rendered}")


def format_filename_timestamp(value: datetime) -> str:
    return value.isoformat(timespec="seconds").replace(":", "-")


def run_id_exists(root: Path, run_id: str) -> bool:
    manifest_root = root / "raw" / "manifests"
    if not manifest_root.exists():
        return False
    for path in manifest_root.rglob("*.json"):
        try:
            manifest = load_json(path)
        except (OSError, json.JSONDecodeError, CollectionError):
            continue
        if manifest.get("run_id") == run_id:
            return True
    return False


def collect(
    config_path: Path,
    root: Path,
    fetcher_factory: Callable[..., BoundedFetcher] = BoundedFetcher,
) -> dict[str, Any]:
    config = load_json(config_path)
    if config.get("status") != "approved_once":
        raise CollectionError("trial configuration is not approved_once")
    run_id = config["run_id"]
    if run_id_exists(root, run_id):
        return {"status": "already_completed", "run_id": run_id, "files_added": []}

    request_policy = config["request_policy"]
    fetcher = fetcher_factory(
        user_agent=request_policy["user_agent"],
        timeout_seconds=request_policy["timeout_seconds"],
        max_response_bytes=request_policy["max_response_bytes"],
        delay_seconds=request_policy["delay_seconds"],
        retries=request_policy["retries"],
    )

    preflight_results: dict[str, str] = {}
    for name in ("robots", "terms"):
        specification = config["preflight"][name]
        body = fetcher.fetch(specification["url"])
        actual_hash = preflight_hash(body, specification)
        if actual_hash != specification["expected_sha256"]:
            raise CollectionError(
                f"{name} content changed since approval: expected "
                f"{specification['expected_sha256']}, got {actual_hash}"
            )
        preflight_results[name] = actual_hash

    started_at = datetime.now(JST).replace(microsecond=0)
    captured_at = started_at.isoformat()
    collector_descriptor = {
        "name": config["collector"]["name"],
        "version": config["collector"]["version"],
    }

    records_by_type: dict[str, list[dict[str, Any]]] = {}
    source_urls: list[str] = []
    for ranking in config["rankings"]:
        ranking_type = ranking["ranking_type"]
        combined: list[dict[str, Any]] = []
        for page in ranking["pages"]:
            body = fetcher.fetch(page["url"])
            source_urls.append(page["url"])
            parsed = parse_ranking_html(
                body,
                ranking_type,
                captured_at,
                run_id,
                collector_descriptor,
            )
            combined.extend(parsed[: page["take"]])

        expected_count = ranking["expected_count"]
        combined = combined[:expected_count]
        actual_ranks = [record["rank"] for record in combined]
        expected_ranks = list(range(1, expected_count + 1))
        if len(combined) != expected_count or actual_ranks != expected_ranks:
            raise CollectionError(
                f"{ranking_type}: expected contiguous ranks 1-{expected_count}, "
                f"got {actual_ranks}"
            )
        records_by_type[ranking_type] = combined

    ranking_validator = load_validator(root / RANKING_SCHEMA)
    manifest_validator = load_validator(root / MANIFEST_SCHEMA)
    for ranking_type, records in records_by_type.items():
        for position, record in enumerate(records, start=1):
            validate_object(ranking_validator, record, f"{ranking_type} record {position}")
            if record["players_online"] > record["players_max"]:
                raise CollectionError(
                    f"{ranking_type} rank {record['rank']}: players_online exceeds players_max"
                )

    date_path = started_at.strftime("%Y/%m/%d")
    filename_timestamp = format_filename_timestamp(started_at)
    files_added: list[str] = []

    with tempfile.TemporaryDirectory(prefix="wayfarer-ranking-collector-") as temporary:
        staging_root = Path(temporary)
        manifest_files: list[dict[str, Any]] = []
        staged_destinations: list[tuple[Path, Path]] = []

        for ranking_type, records in records_by_type.items():
            relative = Path("raw") / "rankings" / date_path / (
                f"{ranking_type}_{filename_timestamp}_{run_id}.jsonl"
            )
            staged = staging_root / relative
            staged.parent.mkdir(parents=True, exist_ok=True)
            staged.write_text(
                "".join(canonical_json_line(record) for record in records),
                encoding="utf-8",
            )
            manifest_files.append(
                {
                    "path": relative.as_posix(),
                    "sha256": sha256_file(staged),
                    "record_type": "minecraft_jp_ranking",
                    "record_count": len(records),
                }
            )
            staged_destinations.append((staged, root / relative))

        finished_at = datetime.now(JST).replace(microsecond=0)
        total_records = sum(len(records) for records in records_by_type.values())
        notes = (
            f"One-time expanded manual trial {config['trial_id']}. "
            f"No direct Server List Ping. Preflight robots={preflight_results['robots']} "
            f"terms={preflight_results['terms']}. Sources: {', '.join(source_urls)}"
        )
        manifest = {
            "schema_version": "1.0.0",
            "record_type": "run_manifest",
            "run_id": run_id,
            "phase": "manual",
            "run_type": "mixed",
            "scheduled_at": config["scheduled_at"],
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "status": "success",
            "expected_targets": total_records,
            "attempted_targets": total_records,
            "successful_targets": total_records,
            "failed_targets": 0,
            "files": manifest_files,
            "collector": {
                "name": config["collector"]["name"],
                "version": config["collector"]["version"],
                "execution_environment": config["collector"]["execution_environment"],
            },
            "notes": notes,
        }
        validate_object(manifest_validator, manifest, "run manifest")

        manifest_relative = Path("raw") / "manifests" / date_path / (
            f"{filename_timestamp}_{run_id}.json"
        )
        staged_manifest = staging_root / manifest_relative
        staged_manifest.parent.mkdir(parents=True, exist_ok=True)
        staged_manifest.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        staged_destinations.append((staged_manifest, root / manifest_relative))

        for _, destination in staged_destinations:
            if destination.exists():
                raise CollectionError(f"refusing to overwrite existing path: {destination}")
        for staged, destination in staged_destinations:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(staged, destination)
            files_added.append(destination.relative_to(root).as_posix())

    return {
        "status": "collected",
        "trial_id": config["trial_id"],
        "run_id": run_id,
        "scheduled_at": config["scheduled_at"],
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "targets_expected": total_records,
        "targets_attempted": total_records,
        "targets_successful": total_records,
        "targets_failed": 0,
        "files_added": files_added,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = collect(args.config.resolve(), args.root.resolve())
    except (CollectionError, OSError, json.JSONDecodeError, KeyError, ValueError) as error:
        print(json.dumps({"status": "failure", "error": str(error)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
