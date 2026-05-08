#!/usr/bin/env python3
"""OpenReview batch submit helper (dry-run first).

Input supports JSON array or JSONL records. Each record should contain:
- title
- abstract
- authors (list[str])
- authorids (list[str], optional)

Default mode is dry-run payload generation.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


def _read_records(path: str) -> list[dict[str, Any]]:
    p = Path(path)
    raw = p.read_text().strip()
    if not raw:
        return []
    if raw.startswith("["):
        data = json.loads(raw)
        if not isinstance(data, list):
            raise ValueError("JSON input must be a list")
        return data

    rows: list[dict[str, Any]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _build_payload(rec: dict[str, Any], invitation: str) -> dict[str, Any]:
    title = rec.get("title", "")
    abstract = rec.get("abstract", "")
    authors = rec.get("authors", [])
    authorids = rec.get("authorids", [])

    if not isinstance(authors, list):
        raise ValueError("authors must be a list")
    if authorids and not isinstance(authorids, list):
        raise ValueError("authorids must be a list")

    return {
        "invitation": invitation,
        "content": {
            "title": {"value": title},
            "abstract": {"value": abstract},
            "authors": {"value": authors},
            "authorids": {"value": authorids},
        },
    }


def _build_client():
    import openreview  # type: ignore

    baseurl = os.environ.get("OPENREVIEW_BASEURL", "https://api2.openreview.net")
    token = os.environ.get("OPENREVIEW_TOKEN")
    username = os.environ.get("OPENREVIEW_USERNAME")
    password = os.environ.get("OPENREVIEW_PASSWORD")

    if token:
        return openreview, openreview.api.OpenReviewClient(baseurl=baseurl, token=token)
    if username and password:
        return openreview, openreview.api.OpenReviewClient(baseurl=baseurl, username=username, password=password)
    raise RuntimeError("Missing OPENREVIEW credentials")


def main() -> int:
    ap = argparse.ArgumentParser(description="OpenReview batch submit helper (dry-run-first)")
    ap.add_argument("--input", required=True, help="Path to JSON array or JSONL")
    ap.add_argument("--invitation", required=True)
    ap.add_argument("--out", default="batch_payloads.json", help="Dry-run payload output")
    ap.add_argument("--apply", action="store_true", help="Apply writes (disabled by default)")
    args = ap.parse_args()

    records = _read_records(args.input)
    payloads = []
    errors = []

    for i, rec in enumerate(records):
        try:
            payloads.append(_build_payload(rec, args.invitation))
        except Exception as exc:
            errors.append({"index": i, "error": str(exc)})

    Path(args.out).write_text(json.dumps({"payloads": payloads, "errors": errors}, ensure_ascii=False, indent=2))
    print(f"[dry-run] prepared payloads: {len(payloads)}, errors: {len(errors)}")
    print(f"[dry-run] output: {args.out}")

    if not args.apply:
        print("[dry-run] no writes performed (use --apply to submit)")
        return 0

    openreview, client = _build_client()
    results = []
    for i, payload in enumerate(payloads):
        try:
            note = openreview.api.Note(invitation=payload["invitation"], content=payload["content"])
            created = client.post_note(note)
            results.append({"index": i, "id": getattr(created, "id", None), "ok": True})
        except Exception as exc:
            results.append({"index": i, "ok": False, "error": str(exc)})

    print(json.dumps({"applied": True, "results": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
