"""`python3 -m common.runners.cli.auth` — connect social accounts.

Three subcommands, because there are genuinely three situations:

    auth --platform threads                 run the OAuth flow in a browser
    auth --platform instagram --paste-token paste a token from the platform's
                                            own token tool (the supported route
                                            wherever loopback redirects are not)
    auth --status                           what is connected, and for how long

Nothing here ever prints a token. `--status` shows a mask and an expiry.
"""

from __future__ import annotations

import argparse
import getpass
import sys
import time

from .. import config, oauth, tokens
from ..errors import RunnerError, TokenError


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="common.runners.cli.auth",
        description="Connect, inspect and disconnect social accounts for publishing.",
    )
    p.add_argument("--platform", help="platform slug (see cli.publish --list-platforms)")
    p.add_argument("--paste-token", action="store_true", help="paste a token instead of running the flow")
    p.add_argument("--expires-in", type=float, help="token lifetime in seconds (with --paste-token)")
    p.add_argument("--status", action="store_true", help="list connected accounts")
    p.add_argument("--revoke", metavar="PLATFORM", help="forget the stored token for a platform")
    p.add_argument("--verify", action="store_true", help="re-check the stored token against the platform")
    return p


def _publisher(name: str):
    config.load_all_publishers()
    try:
        return config.get_publisher(name)
    except KeyError as exc:
        # str(KeyError) re-quotes the message; args[0] is the sentence we wrote.
        raise RunnerError(exc.args[0]) from exc


def cmd_status() -> int:
    print(f"# {tokens.TOKENS_FILE}")
    for line in tokens.status_lines():
        print(line)
    return 0


def cmd_revoke(platform: str) -> int:
    if tokens.remove(platform):
        print(f"Forgot the local token for {platform}.")
        print(
            "Note: this only clears it here. To cut the app's access for good, "
            "remove it in the platform's own app/security settings."
        )
        return 0
    print(f"No stored token for {platform}.", file=sys.stderr)
    return 1


def cmd_verify(platform: str) -> int:
    pub = _publisher(platform)
    try:
        token = tokens.get_valid(platform)
    except TokenError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    try:
        account_id, label = pub.verify_token(token)
    except NotImplementedError:
        print(f"{platform}: no verification endpoint implemented; token is present but unchecked.")
        return 0
    except RunnerError as exc:
        print(f"{platform}: token rejected — {exc}", file=sys.stderr)
        return 2
    print(f"{platform}: OK — {label or account_id}")
    return 0


def cmd_paste(platform: str, expires_in: float | None) -> int:
    pub = _publisher(platform)
    if sys.stdin.isatty():
        token = getpass.getpass(prompt=f"  access token for {platform} (not echoed): ").strip()
    else:
        token = sys.stdin.readline().strip()
    if not token:
        print("empty token — nothing stored", file=sys.stderr)
        return 2

    account_id = label = ""
    try:
        account_id, label = pub.verify_token(token)
    except NotImplementedError:
        print(f"warning: {platform} has no verification endpoint — storing unverified.", file=sys.stderr)
    except RunnerError as exc:
        # Refuse to store a token we already know is bad; the whole point of
        # verifying here is to fail now rather than mid-publish.
        print(f"{platform}: token rejected — {exc}", file=sys.stderr)
        return 2

    tokens.save(
        tokens.TokenEntry(
            platform=platform,
            access_token=token,
            expires_at=(time.time() + expires_in) if expires_in else None,
            account_id=account_id,
            account_label=label,
        )
    )
    where = label or account_id or "(account unknown)"
    print(f"Stored token for {platform} → {where}")
    if not expires_in:
        print("  No expiry recorded. Pass --expires-in <seconds> if this token is short-lived.")
    return 0


def cmd_connect(platform: str) -> int:
    pub = _publisher(platform)
    app = pub.oauth_app()
    if app is None:
        print(
            f"{platform} does not use OAuth — set its keys with skills-keys instead "
            f"({', '.join(pub.requires_env) or 'no keys required'}).",
            file=sys.stderr,
        )
        return 2

    raw = oauth.run_flow(app)
    entry = pub.finalize_auth(raw)
    tokens.save(entry)
    where = entry.account_label or entry.account_id or "(account unknown)"
    print(f"\nConnected {platform} → {where}")
    print(f"  token expires in {entry.expires_in_human()}")
    return 0


def main() -> int:
    args = build_parser().parse_args()
    config.load_all_publishers()

    try:
        if args.status:
            return cmd_status()
        if args.revoke:
            return cmd_revoke(args.revoke)
        if not args.platform:
            print("missing --platform (or use --status / --revoke).", file=sys.stderr)
            return 2
        if args.verify:
            return cmd_verify(args.platform)
        if args.paste_token:
            return cmd_paste(args.platform, args.expires_in)
        return cmd_connect(args.platform)
    except RunnerError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
