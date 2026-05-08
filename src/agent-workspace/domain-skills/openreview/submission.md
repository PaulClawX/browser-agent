# OpenReview submission (domain skill, dry-run-first)

Use this domain skill for OpenReview transfer and batch-submission workflows.

## Scope

- Source note -> target invitation transfer payload generation
- Batch submission payload generation
- Optional write with explicit user approval

## Safety rules

- Dry-run by default (`--apply` absent).
- Never write unless user explicitly asks for `--apply`.
- Validate payload files before applying.
- Keep credentials in environment variables only.

## Prerequisites

- Python 3.11+
- `openreview-py` for `--source-note-id` or `--apply`
- Env vars:
  - `OPENREVIEW_TOKEN` (preferred), or
  - `OPENREVIEW_USERNAME` + `OPENREVIEW_PASSWORD`
  - optional `OPENREVIEW_BASEURL` (default `https://api2.openreview.net`)

## Transfer workflow

```bash
python scripts/or_transfer.py \
  --source-json docs/domain-skills/openreview/examples/source_note.min.json \
  --venue iclr.cc/2027/Conference \
  --invitation iclr.cc/2027/Conference/-/Submission \
  --out transfer_payload.json
```

Review payload:

```bash
cat transfer_payload.json
```

Apply only with explicit confirmation:

```bash
python scripts/or_transfer.py \
  --source-json docs/domain-skills/openreview/examples/source_note.min.json \
  --venue iclr.cc/2027/Conference \
  --invitation iclr.cc/2027/Conference/-/Submission \
  --out transfer_payload.json \
  --apply
```

## Batch workflow

```bash
python scripts/or_batch.py \
  --input docs/domain-skills/openreview/examples/batch.min.jsonl \
  --invitation iclr.cc/2027/Conference/-/Submission \
  --out batch_payloads.json
```

Review payloads/errors:

```bash
cat batch_payloads.json
```

Apply only with explicit confirmation:

```bash
python scripts/or_batch.py \
  --input docs/domain-skills/openreview/examples/batch.min.jsonl \
  --invitation iclr.cc/2027/Conference/-/Submission \
  --out batch_payloads.json \
  --apply
```

## Failure handling

- Missing credentials: stop and request env vars.
- Missing `openreview-py` in apply mode: install dependency.
- Batch validation errors: fix input data and rerun dry-run.

## Minimal examples

- `docs/domain-skills/openreview/examples/source_note.min.json`
- `docs/domain-skills/openreview/examples/batch.min.jsonl`
