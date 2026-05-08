<img src="https://raw.githubusercontent.com/browser-use/media/main/browser-harness/banner-ink.svg" alt="Browser Harness" width="100%" />

# Browser Harness

A thin CDP harness that lets an agent operate your **real Chrome session** directly.

- No wrapped browser automation framework
- No hidden orchestration layer
- Editable task helpers in-repo
- Optimized for agent-driven browser work

## What This Project Is

`browser-harness` is a minimal runtime around Chrome DevTools Protocol (CDP):

- one daemon process for session management
- one Python command (`browser-harness`) for execution
- a compact helper surface for navigation, DOM evaluation, input, tabs, screenshots, uploads, and raw CDP

This design keeps behavior transparent and debuggable while staying easy to extend during real tasks.

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/browser-use/browser-harness
cd browser-harness
uv tool install -e .
```

### 2. Verify install

```bash
command -v browser-harness
browser-harness --version
browser-harness --doctor
```

### 3. Run first command

```bash
browser-harness -c 'print(page_info())'
```

## Browser Connection

`browser-harness` requires a Chrome/Chromium browser with remote debugging available.

### Option A: Connect to your normal Chrome profile (recommended for personal workflows)

1. Open `chrome://inspect/#remote-debugging`
2. Enable `Allow remote debugging for this browser instance`
3. Accept Chrome's allow popup when prompted
4. Re-run:

```bash
browser-harness -c 'print(page_info())'
```

### Option B: Isolated automation profile (no popup workflow)

Launch Chrome manually:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-cdp-profile
```

Then run harness with:

```bash
BU_CDP_URL=http://127.0.0.1:9222 browser-harness -c 'print(page_info())'
```

For full troubleshooting and platform details, read [install.md](install.md).

## Core Usage

Use Python directly:

```bash
browser-harness -c '
new_tab("https://example.com")
wait_for_load()
print(page_info())
'
```

Common helpers:

- `new_tab(url)` / `goto_url(url)`
- `page_info()`
- `click_at_xy(x, y)`
- `type_text(text)` / `press_key(key)`
- `js(expression)`
- `capture_screenshot(path=None)`
- `upload_file(selector, path)`
- `list_tabs()` / `switch_tab(target_id)`
- `cdp(method, **params)` for raw CDP

## Project Structure

- `install.md`: install + browser connection guide
- `SKILL.md`: day-to-day operator guidance
- `src/browser_harness/`: core runtime
- `interaction-skills/`: reusable mechanics playbooks
- `agent-workspace/agent_helpers.py`: editable task-specific helpers
- `agent-workspace/domain-skills/`: optional domain playbooks

## Interaction Skills

Interaction skills capture robust patterns for recurring UI mechanics.

Current set includes:

- connection handling
- dialogs
- downloads
- dropdowns
- iframes / cross-origin iframes
- uploads
- screenshots / viewport / scrolling
- cookies / network requests
- tabs / shadow DOM
- Gemini image generation + editing workflow

See files under [interaction-skills/](interaction-skills/).

## Domain Skills (Optional)

Enable domain-skill hints by setting:

```bash
export BH_DOMAIN_SKILLS=1
```

When enabled, `goto_url` can surface relevant markdown playbooks from `agent-workspace/domain-skills/<site>/`.

## Cloud Browser Mode (Optional)

Use Browser Use Cloud when you need isolated sessions, remote execution, or parallel browsers.

- Set `BROWSER_USE_API_KEY`
- Start daemon with `start_remote_daemon("name")`
- Use `BU_NAME=name` for subsequent commands

## Development

Run tests:

```bash
pytest
```

Install in editable mode for local iteration:

```bash
uv tool install -e .
```

## Contributing

PRs are welcome for:

- helper correctness and stability
- docs and troubleshooting clarity
- new interaction skills
- high-quality domain skills with reproducible site behaviors

When contributing skills, prefer durable selectors/workflows over brittle pixel-only logic.

## License

[MIT](LICENSE)
