#!/usr/bin/env python3
"""Fetch a minimal set of public minecraft.jp pages for parser design.

This is a dry-run probe. It does not write under raw/ and does not parse or
interpret server records.
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://minecraft.jp"
TARGETS = {
    "robots": "/robots.txt",
    "terms": "/terms",
    "score_page_1": "/servers/score",
    "score_page_2": "/servers/score/page:2",
    "player_page_1": "/servers/player",
    "recent_page_1": "/servers/recent",
}
USER_AGENT = (
    "Project-Wayfarer-Research-Trial/1.0 "
    "(+https://github.com/eariver/Project_Wayfarer_Research_Data)"
)
MAX_BYTES = 10 * 1024 * 1024
REQUEST_DELAY_SECONDS = 2.0
TIMEOUT_SECONDS = 30


def fetch(url: str) -> tuple[int, dict[str, str], bytes]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.1",
        },
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        body = response.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise RuntimeError(f"response exceeds {MAX_BYTES} bytes: {url}")
        headers = {key.lower(): value for key, value in response.headers.items()}
        return response.status, headers, body


def main() -> int:
    output = Path("probe-output")
    output.mkdir(parents=True, exist_ok=True)
    summary: dict[str, object] = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "user_agent": USER_AGENT,
        "request_delay_seconds": REQUEST_DELAY_SECONDS,
        "targets": {},
    }

    failures = 0
    for index, (name, path) in enumerate(TARGETS.items()):
        if index:
            time.sleep(REQUEST_DELAY_SECONDS)
        url = BASE_URL + path
        item: dict[str, object] = {"url": url}
        try:
            status, headers, body = fetch(url)
            suffix = ".txt" if name == "robots" else ".html"
            destination = output / f"{name}{suffix}"
            destination.write_bytes(body)
            item.update(
                {
                    "status": status,
                    "content_type": headers.get("content-type"),
                    "content_length": len(body),
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "file": destination.as_posix(),
                }
            )
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, RuntimeError) as error:
            failures += 1
            item.update({"error_type": type(error).__name__, "error": str(error)})
        summary["targets"][name] = item

    (output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
