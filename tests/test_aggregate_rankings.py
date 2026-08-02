from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.aggregate_rankings import write_outputs


class AggregateRankingsTests(unittest.TestCase):
    def test_aggregates_one_ranking_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            input_dir = root / "raw" / "rankings" / "2026" / "08" / "02"
            input_dir.mkdir(parents=True)
            records = [
                {
                    "record_type": "minecraft_jp_ranking",
                    "run_id": "11111111-1111-4111-8111-111111111111",
                    "captured_at": "2026-08-02T20:04:00+09:00",
                    "ranking_type": "score",
                    "rank": 1,
                    "server_id": "server-a",
                    "listing_id": "a",
                    "display_name": "A",
                    "players_online": 12,
                    "players_max": 100,
                    "score": 200.0,
                    "votes_30d": 20,
                    "availability_ratio": 1.0,
                    "tags": ["Survival", "Economy"],
                },
                {
                    "record_type": "minecraft_jp_ranking",
                    "run_id": "11111111-1111-4111-8111-111111111111",
                    "captured_at": "2026-08-02T20:04:00+09:00",
                    "ranking_type": "score",
                    "rank": 2,
                    "server_id": "server-b",
                    "listing_id": "b",
                    "display_name": "B",
                    "players_online": 4,
                    "players_max": 50,
                    "score": 100.0,
                    "votes_30d": 10,
                    "availability_ratio": 0.9,
                    "tags": ["Survival"],
                },
            ]
            source = input_dir / "score.jsonl"
            source.write_text(
                "".join(json.dumps(record) + "\n" for record in records),
                encoding="utf-8",
            )

            output = root / "derived" / "ranking-snapshots"
            write_outputs(root, output)

            result_path = (
                output
                / "2026"
                / "08"
                / "02"
                / "11111111-1111-4111-8111-111111111111_score.json"
            )
            result = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(result["record_count"], 2)
            self.assertEqual(result["total_players_online"], 16)
            self.assertEqual(result["median_players_online"], 8)
            self.assertEqual(result["total_votes_30d"], 30)
            self.assertEqual(result["mean_availability_ratio"], 0.95)
            self.assertEqual(result["tag_counts"][0], {"tag": "Survival", "count": 2})
            self.assertEqual(result["max_players_online"]["server_id"], "server-a")
            self.assertTrue((output / "index.csv").is_file())


if __name__ == "__main__":
    unittest.main()
