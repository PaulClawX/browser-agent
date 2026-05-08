# OpenReview Toolkit (Integrated)

This repository includes a dry-run-first OpenReview toolkit inspired by OpenClaudex/openreview-agent workflows.

## Scripts

- `scripts/or_transfer.py`: transfer/clone a source note into a target invitation payload.
- `scripts/or_batch.py`: prepare and optionally submit batch records.

## Safety defaults

- Both scripts are **dry-run by default**.
- No write happens unless `--apply` is provided.
- Credentials are read from env vars only.

## Env vars

- `OPENREVIEW_BASEURL` (optional, default `https://api2.openreview.net`)
- `OPENREVIEW_TOKEN` (preferred)
- or `OPENREVIEW_USERNAME` + `OPENREVIEW_PASSWORD`

## Quick examples

```bash
python scripts/or_transfer.py \
  --source-json ./source_note.json \
  --venue iclr.cc/2027/Conference \
  --invitation iclr.cc/2027/Conference/-/Submission \
  --out transfer_payload.json

python scripts/or_batch.py \
  --input ./batch.jsonl \
  --invitation iclr.cc/2027/Conference/-/Submission \
  --out batch_payloads.json
```
