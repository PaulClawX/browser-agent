"""Agent-editable browser helpers.

Add task-specific browser primitives here. Core helpers from browser_harness.helpers
load this file when BH_AGENT_WORKSPACE points at this directory, or when this
repo's default agent-workspace exists.
"""

import time


def github_create_org_repo(org, repo, description="", private=True, retries=3):
    """Create an org repo on GitHub UI and verify landing URL.

    Returns:
      dict(ok=bool, url=str, errors=list[str], attempts=list[dict])
    """
    from browser_harness import helpers as h

    h.new_tab(f"https://github.com/organizations/{org}/repositories/new")
    h.wait_for_load(20)
    h.wait(1.5)

    attempts = []
    last_errors = []

    for i in range(1, retries + 1):
        # Dismiss transient flash errors from previous attempts.
        h.js(
            """
(() => {
  document.querySelectorAll('button.flash-close, .js-ajax-error-dismiss').forEach(b => b.click());
})()
"""
        )
        h.wait(0.3)

        state = h.js(
            """
(() => {
  const out = {};
  out.url = location.href;
  out.isLogin = location.pathname.includes('/login') || !!document.querySelector('input[name="login"]');
  out.nameInput = !!document.querySelector('#repository-name-input');
  out.ownerBtn = !!Array.from(document.querySelectorAll('button')).find(
    b => (b.getAttribute('aria-label') || '').toLowerCase().includes('owner')
  );
  out.createBtn = !!Array.from(document.querySelectorAll('button[type="submit"]')).find(
    b => /create repository/i.test((b.innerText || '').trim())
  );
  out.errors = Array.from(document.querySelectorAll('[role=alert], .flash-error, .flash'))
    .map(e => (e.innerText || '').trim())
    .filter(Boolean)
    .slice(0, 8);
  return out;
})()
"""
        )

        if state.get("isLogin"):
            return {
                "ok": False,
                "url": state.get("url", ""),
                "errors": ["GitHub login required"],
                "attempts": attempts,
            }

        # Fill repository name/description and visibility, then submit.
        submit = h.js(
            f"""
(() => {{
  const out = {{ok:false, reason:'', disabled:null}};
  const input = document.querySelector('#repository-name-input');
  if (!input) {{ out.reason = 'missing-repository-name-input'; return out; }}
  input.focus();
  input.value = '';
  input.dispatchEvent(new Event('input', {{ bubbles: true }}));
  input.value = {repo!r};
  input.dispatchEvent(new Event('input', {{ bubbles: true }}));
  input.dispatchEvent(new Event('change', {{ bubbles: true }}));

  const desc = document.querySelector('input[name="Description"], #_r_d_');
  if (desc) {{
    desc.focus();
    desc.value = {description!r};
    desc.dispatchEvent(new Event('input', {{ bubbles: true }}));
    desc.dispatchEvent(new Event('change', {{ bubbles: true }}));
  }}

  const owner = Array.from(document.querySelectorAll('button'))
    .find(b => ((b.getAttribute('aria-label') || '') + ' ' + (b.innerText || '')).toLowerCase().includes('owner'));
  if (owner && !((owner.innerText || '') + ' ' + (owner.getAttribute('aria-label') || '')).includes({org!r})) {{
    owner.click();
    const orgOpt = Array.from(document.querySelectorAll('[role="option"], button, span, div'))
      .find(e => ((e.innerText || '') + ' ' + (e.getAttribute('aria-label') || '')).includes({org!r}));
    if (orgOpt) orgOpt.click();
  }}

  if ({'true' if private else 'false'}) {{
    const privateBtn = Array.from(document.querySelectorAll('button'))
      .find(b => /private/i.test((b.innerText || '').trim()));
    if (privateBtn) privateBtn.click();
  }}

  const create = Array.from(document.querySelectorAll('button[type="submit"]'))
    .find(b => /create repository/i.test((b.innerText || '').trim()));
  if (!create) {{ out.reason = 'missing-create-button'; return out; }}
  out.disabled = !!create.disabled;
  if (create.disabled) {{ out.reason = 'create-disabled'; return out; }}
  create.click();
  out.ok = true;
  return out;
}})()
"""
        )
        h.wait(2.5)

        url = h.js("location.href")
        errs = h.js(
            """
(() => Array.from(document.querySelectorAll('[role=alert], .flash-error, .flash'))
  .map(e => (e.innerText || '').trim())
  .filter(Boolean)
  .slice(0, 8))()
"""
        )
        last_errors = errs or []
        attempt = {"attempt": i, "submit": submit, "url": url, "errors": errs}
        attempts.append(attempt)

        # Success condition: we left /repositories/new and reached target repo URL.
        if f"github.com/{org}/{repo}" in url and "/repositories/new" not in url:
            return {"ok": True, "url": url, "errors": [], "attempts": attempts}

        # Hard platform error often means org permission/policy; break early.
        if any("can’t perform that action" in e.lower() or "can't perform that action" in e.lower() for e in last_errors):
            break

        time.sleep(0.8)

    return {
        "ok": False,
        "url": h.js("location.href"),
        "errors": last_errors,
        "attempts": attempts,
    }


def ask_user(prompt, expect="done"):
    """Block on stdin until the user replies. Bring Chrome to the front first.

    The agent decides *when* to call this (e.g. it sees a login wall, captcha,
    2FA, or any state it can't resolve). The helper only handles the mechanics
    of getting the user's attention and reading the reply.

    Returns the stripped stdin line. If the user just hits Enter, returns `expect`.
    """
    import shutil, subprocess, sys

    if sys.platform == "darwin" and shutil.which("osascript"):
        subprocess.run(
            ["osascript", "-e", 'tell application "Google Chrome" to activate'],
            check=False,
        )
    sys.stderr.write(f"\n[browser-agent needs you] {prompt}\n  reply (Enter = '{expect}'): ")
    sys.stderr.flush()
    try:
        reply = sys.stdin.readline().strip()
    except (EOFError, KeyboardInterrupt):
        reply = ""
    return reply or expect
