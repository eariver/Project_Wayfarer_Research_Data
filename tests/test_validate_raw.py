from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from tools.validate_raw import (
    RepositoryValidationError,
    resolve_manifest_path,
    validate_cross_field_invariants,
    validate_repository,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class ValidateRawTests(unittest.TestCase):
    def test_repository_samples_are_valid(self) -> None:
        file_count, record_count = validate_repository(
            REPOSITORY_ROOT,
            ["samples"],
        )
        self.assertEqual(file_count, 3)
        self.assertEqual(record_count, 4)

    def test_orphan_raw_observation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            shutil.copytree(
                REPOSITORY_ROOT / "collector-contract",
                root / "collector-contract",
            )
            polling_directory = root / "raw" / "polling" / "2026" / "08" / "02"
            polling_directory.mkdir(parents=True)
            shutil.copyfile(
                REPOSITORY_ROOT / "samples" / "server-ping-records.jsonl",
                polling_directory / "orphan.jsonl",
            )

            with self.assertRaisesRegex(
                RepositoryValidationError,
                "not referenced by a manifest",
            ):
                validate_repository(root, ["raw"])

    def test_manifest_path_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            manifest_path = root / "samples" / "run-manifest.json"

            with self.assertRaisesRegex(
                RepositoryValidationError,
                "must remain inside the repository",
            ):
                resolve_manifest_path(
                    root,
                    manifest_path,
                    "raw/../../outside.jsonl",
                )

    def test_duplicate_manifest_file_paths_are_rejected(self) -> None:
        record = {
            "record_type": "run_manifest",
            "files": [
                {"path": "samples/data.jsonl"},
                {"path": "samples/data.jsonl"},
            ],
        }

        with self.assertRaisesRegex(
            RepositoryValidationError,
            "manifest file paths must be unique",
        ):
            validate_cross_field_invariants(
                Path("samples/run-manifest.json"),
                1,
                record,
            )

    def test_ranking_player_count_above_listed_maximum_is_preserved(self) -> None:
        record = {
            "record_type": "minecraft_jp_ranking",
            "players_online": 65,
            "players_max": 0,
        }

        validate_cross_field_invariants(
            Path("samples/ranking.jsonl"),
            1,
            record,
        )

    def test_direct_ping_player_count_above_maximum_is_rejected(self) -> None:
        record = {
            "record_type": "server_ping",
            "result": "success",
            "online_players": 11,
            "max_players": 10,
        }

        with self.assertRaisesRegex(
            RepositoryValidationError,
            "online_players",
        ):
            validate_cross_field_invariants(
                Path("samples/server-ping.jsonl"),
                1,
                record,
            )


if __name__ == "__main__":
    unittest.main()
