#!/usr/bin/env python3
"""Aggregate immutable minecraft.jp ranking snapshots into deterministic summaries."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: record must be an object")
            yield value


def normalize_number(value: float | int | None) -> float | int | None:
    if value is None:
        return None
    if isinstance(value, float):
        value = round(value, 6)
        if value.is_integer():
            return int(value)
    return value


def aggregate_group(
    run_id: str,
    ranking_type: str,
    records: list[dict[str, Any]],
    source_files: set[str],
) -> dict[str, Any]:
    ordered = sorted(records, key=lambda item: (item["rank"], item["listing_id"]))
    players = [item["players_online"] for item in ordered if item["players_online"] is not None]
    player_caps = [item["players_max"] for item in ordered if item["players_max"] is not None]
    scores = [item["score"] for item in ordered if item["score"] is not None]
    votes = [item["votes_30d"] for item in ordered if item["votes_30d"] is not None]
    availability = [
        item["availability_ratio"]
        for item in ordered
        if item["availability_ratio"] is not None
    ]
    tags = Counter(tag for item in ordered for tag in item.get("tags", []))
    captures = sorted({item["captured_at"] for item in ordered})

    max_player_record = None
    if players:
        max_player_record = max(
            (item for item in ordered if item["players_online"] is not None),
            key=lambda item: (item["players_online"], -item["rank"]),
        )

    return {
        "schema_version": "1.0.0",
        "derived_type": "ranking_snapshot_summary",
        "run_id": run_id,
        "ranking_type": ranking_type,
        "captured_at_min": captures[0],
        "captured_at_max": captures[-1],
        "record_count": len(ordered),
        "records_with_players": len(players),
        "total_players_online": sum(players),
        "mean_players_online": normalize_number(statistics.fmean(players)) if players else None,
        "median_players_online": normalize_number(statistics.median(players)) if players else None,
        "total_listed_capacity": sum(player_caps),
        "mean_score": normalize_number(statistics.fmean(scores)) if scores else None,
        "total_votes_30d": sum(votes),
        "mean_availability_ratio": (
            normalize_number(statistics.fmean(availability)) if availability else None
        ),
        "max_players_online": (
            {
                "server_id": max_player_record.get("server_id"),
                "listing_id": max_player_record["listing_id"],
                "display_name": max_player_record["display_name"],
                "players_online": max_player_record["players_online"],
                "rank": max_player_record["rank"],
            }
            if max_player_record
            else None
        ),
        "tag_counts": [
            {"tag": tag, "count": count}
            for tag, count in sorted(tags.items(), key=lambda item: (-item[1], item[0]))
        ],
        "top_by_rank": [
            {
                "rank": item["rank"],
                "server_id": item.get("server_id"),
                "listing_id": item["listing_id"],
                "display_name": item["display_name"],
                "players_online": item["players_online"],
                "players_max": item["players_max"],
                "score": item["score"],
                "votes_30d": item["votes_30d"],
            }
            for item in ordered[:10]
        ],
        "source_files": sorted(source_files),
    }


def load_groups(
    root: Path,
    input_dir: Path,
) -> dict[tuple[str, str], tuple[list[dict[str, Any]], set[str]]]:
    groups: dict[tuple[str, str], tuple[list[dict[str, Any]], set[str]]] = {}
    paths = sorted(input_dir.rglob("*.jsonl")) if input_dir.exists() else []
    for path in paths:
        relative = path.relative_to(root).as_posix()
        for record in iter_jsonl(path):
            if record.get("record_type") != "minecraft_jp_ranking":
                continue
            key = (record["run_id"], record["ranking_type"])
            if key not in groups:
                groups[key] = ([], set())
            groups[key][0].append(record)
            groups[key][1].add(relative)
    return groups


def write_outputs(root: Path, output_dir: Path) -> list[Path]:
    groups = load_groups(root, root / "raw" / "rankings")
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, Any]] = []
    written: list[Path] = []

    for (run_id, ranking_type), (records, source_files) in sorted(groups.items()):
        summary = aggregate_group(run_id, ranking_type, records, source_files)
        date = summary["captured_at_min"][:10].replace("-", "/")
        destination = output_dir / date / f"{run_id}_{ranking_type}.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        summaries.append(summary)
        written.append(destination)

    index_path = output_dir / "index.csv"
    with index_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "run_id",
            "ranking_type",
            "captured_at_min",
            "captured_at_max",
            "record_count",
            "records_with_players",
            "total_players_online",
            "mean_players_online",
            "median_players_online",
            "total_listed_capacity",
            "mean_score",
            "total_votes_30d",
            "mean_availability_ratio",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for summary in summaries:
            writer.writerow({field: summary[field] for field in fieldnames})
    written.append(index_path)
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("derived/ranking-snapshots"),
        help="Output path relative to repository root unless absolute.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    written = write_outputs(root, output)
    print(f"wrote {len(written)} derived ranking files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
