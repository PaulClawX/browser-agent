# Gemini image generation + editing (gemini.google.com)

Use this playbook when the user wants **image generation** or **image editing** on Gemini, and asks for strict guarantees around upload-before-generate and deterministic download.

## Goals

- Generate an image from prompt on Gemini.
- Edit an existing image with prompt + reference.
- Enforce: `upload must succeed before submit`.
- Download final generated image to local disk.

## Preconditions

- User is already logged into `https://gemini.google.com/app`.
- A local reference image exists (absolute path), e.g. `/path/to/reference.jpg`.
- Browser harness daemon is connected (`browser-agent --doctor` shows chrome ok, daemon ok).

## Reliability rules (non-negotiable)

- Never submit prompt before upload is verified.
- Treat upload as failed unless at least one verification signal is observed.
- If upload is uncertain, retry upload flow; do not proceed.

## Upload verification signals

Use one or more of these before prompt submit:

1. New attachment chip appears near the composer.
2. New thumbnail appears in composer area.
3. File chooser path succeeded via direct file input set.
4. Composer/attachment area text changes to include image/attachment/remove markers.

If none are true, upload is not confirmed.

## Recommended flow

1. Open new tab to Gemini:

```python
new_tab("https://gemini.google.com/app")
wait_for_load(20)
```

2. Start a clean chat (`New chat`) and optionally click `Create image`.

3. Open upload menu:

- Click button with aria-label matching `Open upload file menu`.
- Click menu item matching `Upload files`.

4. Upload reference image:

- Preferred: `upload_file("input[type='file']...", "/abs/path/ref.jpg")` when input exists.
- If no file input appears immediately, short polling + retry menu open/click.

5. Verify upload signals (strict gate).

6. Submit prompt only after gate passes.

7. Wait for generation completion:

- Poll page text for `creating/generating/working` states.
- Detect new `blob:` image source in DOM.

8. Download final image:

- Convert target `blob:` image to PNG via canvas + `toDataURL`.
- Decode and write to local file in `output/`.

## Prompt template for reference fusion

Use language that forces identity consistency:

- `Use the uploaded portrait as a strict identity reference.`
- `Preserve recognizable facial structure, side-profile silhouette, and proportions.`
- `Fuse identity features while keeping artistic style constraints.`

## Failure handling

- If upload cannot be confirmed after retries: stop and report failure explicitly.
- If Gemini stalls: retry once in a fresh chat.
- If only avatar blobs are found: keep polling until a larger generation blob appears.

## Download verification

After save, verify locally:

- file type is PNG/JPEG image (not HTML)
- expected pixel size > avatar size (e.g. not 64x64)
- reasonable file size (non-trivial)

## Anti-patterns

- Submitting prompt before upload confirmation.
- Trusting only page title text as upload proof.
- Saving every URL blindly (can capture HTML/account endpoints).
