# Auth walls

When a navigation lands on a login page, OAuth/SSO consent, captcha, 2FA, or
any "you must be a human" gate. The harness deliberately doesn't auto-detect
these — you (the agent) decide. This file is the playbook.

## Decision order

1. **Avoid the wall: reuse a logged-in profile.**
   Most "I hit a login page" problems disappear if a profile with the right
   cookies is already in the cloud. See `profile-sync.md` for the chat-driven
   flow. Pattern:
   ```python
   profiles = list_cloud_profiles()
   # show user; let them pick or sync a local one; then:
   start_remote_daemon("work", profileName="<picked>")
   ```
   Don't sync silently — cookies are real auth.

2. **If you actually need the user, ask once and block.**
   Use `ask_user()` from `src/agent-workspace/agent_helpers.py`. Bring Chrome
   to the front, tell the user *exactly* what to do, then read one line:
   ```python
   from agent_helpers import ask_user
   ask_user("Sign in to GitHub in the front Chrome window, then press Enter.")
   ```
   `ask_user` returns whatever the user typed (default `"done"` on Enter), so
   you can branch on `"skip"`, `"abort"`, or free text.

3. **Don't type credentials from screenshots.** Reaffirmed from `SKILL.md`.

## Signals that usually mean "auth wall" (for the agent's eyes only)

Use these as hints when reading a screenshot or `page_info()` — not as a
hard-coded detector. Two or more is a strong signal.

- URL contains `/login`, `/signin`, `/sign_in`, `accounts.google.`,
  `login.microsoftonline.`, `oauth/authorize`, `/saml`, `/sso`, or your
  company's IdP host.
- OAuth params present: `client_id=` together with `redirect_uri=` and
  `response_type=`.
- A visible `<input type="password">`, or a form whose `action` contains
  `login` / `signin`.
- `<title>` or a prominent heading reads "Sign in" / "Log in" / "登录".
- HTTP 401/403 on the resource you actually wanted (check via
  `Network.getResponseBody` or `http_get` for static endpoints).

## Things that *aren't* login walls but need the same treatment

`ask_user` is the right tool for any "agent can't proceed without the human":

- Captcha / hCaptcha / Cloudflare turnstile
- 2FA code prompt (TOTP, SMS, push notification)
- Email-link verification
- Geo / device-risk challenge ("Was this you?")
- Payment confirmation pages
- Anything where typing from a screenshot would be unsafe

## Resume pattern after the user finishes

Many SSO flows redirect back automatically. Verify before assuming:

```python
from agent_helpers import ask_user
goto_url(target); wait_for_load()
# ...you decide it's a wall...
ask_user(f"Sign in so I can reach {target}, then press Enter.")
wait_for_load()
if target not in page_info()["url"]:
    goto_url(target); wait_for_load()
capture_screenshot()  # verify you're on the right page now
```

## What this skill does *not* do

- No background detector loop. Auth walls are an agent-level decision, not a
  framework one.
- No retry manager. If the user types `"abort"`, stop and report.
- No credential storage. Use `profile-sync` for persistent login state.
