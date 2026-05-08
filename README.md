# Browser Agent

<p align="center">
  <img src="https://raw.githubusercontent.com/browser-use/media/main/browser-agent/banner-ink.svg" alt="Browser Agent cover" width="100%">
</p>

<p align="center">
  <strong>CDP-native browser automation runtime for agents, with editable skills and reliable Gemini image workflows.</strong>
</p>

<p align="center">
  • Real Chrome Control • Skill-Driven Automation • Upload-Verified Image Generation •
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-workflows">Workflows</a> •
  <a href="#-safety-model">Safety Model</a> •
  <a href="SKILL.md">Agent Guide</a>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-green"></a>
  <img alt="Status" src="https://img.shields.io/badge/status-0.1.0--alpha-orange">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9%2B-blue">
  <img alt="CDP" src="https://img.shields.io/badge/CDP-native-111827">
  <img alt="Codex" src="https://img.shields.io/badge/Codex-skill--ready-111827">
</p>

## Quick Navigation

> [!TIP]
> **I'm a human** -> Read this README for install, setup, and safe workflows.
>
> **I'm an agent** -> Read [SKILL.md](SKILL.md) for operation rules and execution patterns.

`browser-agent` is a minimal runtime that lets agents control your real Chrome session directly over CDP, while keeping task logic editable in-repo.

- **For operators**: one command surface for browser actions, diagnostics, and updates.
- **For agents**: stable helper APIs (`new_tab`, `js`, `click_at_xy`, `upload_file`, raw `cdp`).
- **For reliability**: interaction skills and domain skills to encode repeatable mechanics.

## Quick Start

Tell your coding agent:

> Install Browser Agent from `https://github.com/PaulClawX/browser-agent` and set it up to control my Chrome via CDP.

### 1) Install

```bash
git clone https://github.com/PaulClawX/browser-agent
cd browser-agent
uv tool install -e .
```

### 2) Verify

```bash
command -v browser-agent
browser-agent --version
browser-agent --doctor
```

### 3) First command

```bash
browser-agent -c 'print(page_info())'
```

## Browser Connection

### Option A: attach to your normal Chrome profile

1. Open `chrome://inspect/#remote-debugging`
2. Enable `Allow remote debugging for this browser instance`
3. Accept the Chrome allow popup when prompted
4. Re-run:

```bash
browser-agent -c 'print(page_info())'
```

### Option B: isolated profile on a dedicated port

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-cdp-profile

BU_CDP_URL=http://127.0.0.1:9222 browser-agent -c 'print(page_info())'
```

For full setup and troubleshooting, see [install.md](install.md).

## Features

- Direct CDP control against real Chrome tabs.
- Minimal daemon + IPC architecture.
- Rich helper APIs for navigation, DOM eval, input, uploads, screenshots, tabs.
- Interaction skills for repeatable UI mechanics.
- Domain skills for site-specific workflows.
- Gemini image generation/editing workflow with upload verification gate.

## Workflows

| Tier | Workflow | Expected Behavior |
|---|---|---|
| Stable | General browser automation | Deterministic tab + DOM + input operations through CDP helpers |
| Stable | Upload-driven tasks | Upload confirmation before submit; fail-fast if upload isn't verifiable |
| Stable | Gemini image generation/editing | Prompt + reference flow with strict upload-first gating and export |
| Stable | Diagnostics and lifecycle | `--doctor`, daemon auto-start, update checks |
| Best-effort | Complex anti-bot sites | Fallback to coordinate actions, retries, and skill-specific patterns |

## Safety Model

- **Connect to an already-running user browser.** Do not silently launch hidden browsers for user tasks.
- **Upload-first guarantees for image tasks.** Never submit generation prompts before attachment verification.
- **Human-in-the-loop for auth.** If login walls or security prompts appear, pause and ask the user.
- **No secret persistence.** Do not commit credentials, cookies, or private tokens into repo files.
- **Verify outcomes visibly.** Re-check screenshots/page state after meaningful actions.

## Core Command Pattern

```bash
browser-agent -c '
new_tab("https://example.com")
wait_for_load()
print(page_info())
'
```

Common helpers:

- `new_tab(url)`, `goto_url(url)`
- `page_info()`, `wait_for_load()`, `wait_for_element()`
- `click_at_xy(x, y)`, `type_text(text)`, `press_key(key)`
- `js(expression)`, `cdp(method, **params)`
- `upload_file(selector, path)`
- `capture_screenshot(path=None)`

## Project Layout

- `src/browser_harness/` - core runtime modules
- `SKILL.md` - operator rules for day-to-day use
- `install.md` - first-time install and connection
- `interaction-skills/` - reusable browser mechanics playbooks
- `agent-workspace/agent_helpers.py` - task-specific helper extensions
- `agent-workspace/domain-skills/` - site-specific playbooks

## Interaction Skills

See [interaction-skills/](interaction-skills/) for practical playbooks, including:

- connection, dialogs, dropdowns, uploads
- tabs, iframes, cross-origin iframes, shadow DOM
- screenshots, scrolling, viewport
- Gemini image generation + editing

## Domain Skills

Enable domain hinting:

```bash
export BH_DOMAIN_SKILLS=1
```

When enabled, `goto_url` can surface relevant files from `agent-workspace/domain-skills/<site>/`.

## Cloud Mode (Optional)

With `BROWSER_USE_API_KEY`, you can run isolated remote browsers:

- `start_remote_daemon("work")`
- `BU_NAME=work browser-agent -c 'print(page_info())'`



## License

[MIT](LICENSE)

## OpenReview Toolkit

This repository now includes a dry-run-first OpenReview toolkit.

- `scripts/or_transfer.py`: source note transfer payload generation + optional apply
- `scripts/or_batch.py`: batch payload generation + optional apply
- Docs: `docs/openreview/README.md`

Both commands default to dry-run. Writes happen only with `--apply`.
