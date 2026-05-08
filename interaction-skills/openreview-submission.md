# OpenReview submission (dry-run-first)

Use this skill when the user wants to transfer an existing submission to a new venue,
or create batch submissions with explicit safety gates.

## Scope

- Source note -> target invitation transfer payload
- Batch submission payload generation
- Optional write to OpenReview only when explicitly requested

## Safety rules

- Default mode is dry-run (`--apply` absent).
- Never run `--apply` unless the user explicitly asks to write.
- Validate payload output files before any write.
- Keep credentials in environment variables only.

## Prerequisites

- Python 3.11+
- Optional: `openreview-py` if using `--source-note-id` or `--apply`
- Credentials:
  - `OPENREVIEW_TOKEN` (preferred), or
  - `OPENREVIEW_USERNAME` + `OPENREVIEW_PASSWORD`
  - Optional `OPENREVIEW_BASEURL` (default `https://api2.openreview.net`)

## Transfer workflow

1. Prepare transfer payload from source JSON:

```bash
python scripts/or_transfer.py \
  --source-json docs/openreview/examples/source_note.min.json \
  --venue iclr.cc/2027/Conference \
  --invitation iclr.cc/2027/Conference/-/Submission \
  --out transfer_payload.json
```

2. Inspect generated payload:

```bash
cat transfer_payload.json
```

3. Apply only with explicit user confirmation:

```bash
python scripts/or_transfer.py \
  --source-json docs/openreview/examples/source_note.min.json \
  --venue iclr.cc/2027/Conference \
  --invitation iclr.cc/2027/Conference/-/Submission \
  --out transfer_payload.json \
  --apply
```

## Batch workflow

1. Build batch payloads from minimal JSONL:

```bash
python scripts/or_batch.py \
  --input docs/openreview/examples/batch.min.jsonl \
  --invitation iclr.cc/2027/Conference/-/Submission \
  --out batch_payloads.json
```

2. Review payloads and validation errors:

```bash
cat batch_payloads.json
```

3. Apply only with explicit user confirmation:

```bash
python scripts/or_batch.py \
  --input docs/openreview/examples/batch.min.jsonl \
  --invitation iclr.cc/2027/Conference/-/Submission \
  --out batch_payloads.json \
  --apply
```

## Failure handling

- Missing credentials: stop and ask user to set env vars.
- Missing `openreview` package in apply mode: ask user to install `openreview-py`.
- Batch validation errors: fix input records and rerun dry-run.

## Minimal checklist before write

- Target `--invitation` is correct.
- Authors/authorids look correct in dry-run payload.
- User explicitly asked to run `--apply`.
