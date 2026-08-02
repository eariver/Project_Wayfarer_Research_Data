from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.collect_minecraft_jp_rankings import CollectionError, collect, parse_ranking_html


def ranking_html(start_rank: int, count: int, prefix: str = "server") -> bytes:
    rows = []
    for offset in range(count):
        rank = start_rank + offset
        online = 0 if rank == start_rank else rank
        rows.append(
            f"""
            <tr class="row-info">
              <td class="rank"><span>#{rank}</span></td>
              <td class="name"><span class="label">1.21.{rank}</span><a href="/servers/{prefix}-{rank}">{prefix} {rank}</a></td>
              <td class="address">{prefix}-{rank}.example</td>
              <td class="players">{online}<span class="muted"> / 100</span></td>
              <td class="uptime"><div class="bar">99%</div></td>
              <td class="score">{1000-rank}.5</td>
              <td class="vote">{rank:,}</td>
            </tr>
            <tr class="row-tags"><td class="tags"><span class="tags-collapse"><span class="label">サバイバル</span><span class="label">経済</span></span></td></tr>
            """
        )
    return ("<table class='table-servers'><tbody>" + "".join(rows) + "</tbody></table>").encode()


class FakeFetcher:
    responses: dict[str, bytes] = {}

    def __init__(self, **_: object) -> None:
        pass

    def fetch(self, url: str, accept: str = "") -> bytes:
        del accept
        if url not in self.responses:
            raise CollectionError(f"unexpected URL: {url}")
        return self.responses[url]


class RankingCollectorTests(unittest.TestCase):
    def test_parser_preserves_zero_players_and_fields(self) -> None:
        records = parse_ranking_html(
            ranking_html(1, 2),
            "score",
            "2026-08-02T20:17:00+09:00",
            "11111111-1111-4111-8111-111111111111",
            {"name": "test", "version": "1.0.0"},
        )
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["players_online"], 0)
        self.assertEqual(records[0]["players_max"], 100)
        self.assertIsNone(records[0]["server_id"])
        self.assertEqual(records[0]["tags"], ["サバイバル", "経済"])
        self.assertEqual(records[1]["rank"], 2)

    def test_collects_three_rankings_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(Path("collector-contract"), root / "collector-contract")
            robots = b"robots"
            terms = b"terms"
            FakeFetcher.responses = {
                "https://example.test/robots": robots,
                "https://example.test/terms": terms,
                "https://example.test/score": ranking_html(1, 3, "score"),
                "https://example.test/player": ranking_html(1, 2, "player"),
                "https://example.test/recent": ranking_html(1, 2, "recent"),
            }
            config = {
                "schema_version": "1.0.0",
                "trial_id": "test-expanded",
                "status": "approved_once",
                "run_id": "22222222-2222-4222-8222-222222222222",
                "scheduled_at": "2026-08-02T20:17:00+09:00",
                "collector": {
                    "name": "test-collector",
                    "version": "1.0.0",
                    "execution_environment": "unit test",
                },
                "request_policy": {
                    "user_agent": "test",
                    "timeout_seconds": 1,
                    "max_response_bytes": 100000,
                    "delay_seconds": 0,
                    "retries": 0,
                },
                "preflight": {
                    "robots": {
                        "url": "https://example.test/robots",
                        "expected_sha256": hashlib.sha256(robots).hexdigest(),
                    },
                    "terms": {
                        "url": "https://example.test/terms",
                        "expected_sha256": hashlib.sha256(terms).hexdigest(),
                    },
                },
                "rankings": [
                    {
                        "ranking_type": "score",
                        "expected_count": 3,
                        "pages": [{"url": "https://example.test/score", "take": 3}],
                    },
                    {
                        "ranking_type": "player",
                        "expected_count": 2,
                        "pages": [{"url": "https://example.test/player", "take": 2}],
                    },
                    {
                        "ranking_type": "recent",
                        "expected_count": 2,
                        "pages": [{"url": "https://example.test/recent", "take": 2}],
                    },
                ],
            }
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")

            report = collect(config_path, root, fetcher_factory=FakeFetcher)
            self.assertEqual(report["status"], "collected")
            self.assertEqual(report["targets_successful"], 7)
            ranking_files = sorted((root / "raw" / "rankings").rglob("*.jsonl"))
            self.assertEqual(len(ranking_files), 3)
            manifest_files = list((root / "raw" / "manifests").rglob("*.json"))
            self.assertEqual(len(manifest_files), 1)
            manifest = json.loads(manifest_files[0].read_text(encoding="utf-8"))
            self.assertEqual(manifest["run_type"], "mixed")
            self.assertEqual(manifest["expected_targets"], 7)
            self.assertEqual(len(manifest["files"]), 3)

            second = collect(config_path, root, fetcher_factory=FakeFetcher)
            self.assertEqual(second["status"], "already_completed")

    def test_preflight_change_stops_before_raw_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(Path("collector-contract"), root / "collector-contract")
            FakeFetcher.responses = {
                "https://example.test/robots": b"changed",
                "https://example.test/terms": b"terms",
            }
            config = {
                "status": "approved_once",
                "trial_id": "test",
                "run_id": "33333333-3333-4333-8333-333333333333",
                "scheduled_at": "2026-08-02T20:17:00+09:00",
                "collector": {
                    "name": "test",
                    "version": "1",
                    "execution_environment": "test",
                },
                "request_policy": {
                    "user_agent": "test",
                    "timeout_seconds": 1,
                    "max_response_bytes": 1000,
                    "delay_seconds": 0,
                    "retries": 0,
                },
                "preflight": {
                    "robots": {
                        "url": "https://example.test/robots",
                        "expected_sha256": "0" * 64,
                    },
                    "terms": {
                        "url": "https://example.test/terms",
                        "expected_sha256": hashlib.sha256(b"terms").hexdigest(),
                    },
                },
                "rankings": [],
            }
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaises(CollectionError):
                collect(config_path, root, fetcher_factory=FakeFetcher)
            self.assertFalse((root / "raw").exists())


if __name__ == "__main__":
    unittest.main()
