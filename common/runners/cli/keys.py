"""Keys CLI — manage ~/.skills.env (the runner's key store).

Subcommands:
  list                       Print current keys with masked values + verify status (lazy)
  add <NAME> [<VALUE>]       Add/update a key. Without VALUE, prompts silently via stdin.
  update <NAME> [<VALUE>]    Alias for add (same semantics).
  remove <NAME>              Remove a key.
  enable <NAME>              Shortcut: upsert NAME=1 (for *_ENABLED gate flags).
  disable <NAME>             Shortcut: remove NAME (or set to 0). We remove.
  verify [<NAME>...]         Ping providers and report valid / invalid / unknown.
  path                       Print absolute path of the keys file.
  export [--mask]            Print eval-ready `export NAME="VALUE"` lines.

Storage: ~/.skills.env (override with SKILLS_KEYS_FILE), chmod 600. Loaded
into os.environ at every runner CLI startup. Explicit shell exports win
over file entries.
"""

from __future__ import annotations

import argparse
import getpass
import re
import sys
from pathlib import Path

from .. import keysfile
from .. import verify as verify_mod


_KNOWN_ENVS = [
    "OPENAI_API_KEY",
    "OPENAI_SORA_API_ENABLED",
    "GEMINI_API_KEY",
    "LYRIA_API_ENABLED",
    "ANTHROPIC_API_KEY",
    "BFL_API_KEY",
    "FAL_KEY",
    "REPLICATE_API_TOKEN",
    "RUNWAY_API_KEY",
    "KLING_ACCESS_KEY_ID",
    "KLING_ACCESS_KEY_SECRET",
    "KLING_API_HOST",
    "SUNO_API_KEY",
    "SUNO_API_URL",
    "SUNO_API_ENABLED",
    "ELEVENLABS_API_KEY",
    "IDEOGRAM_API_KEY",
    "S3_BUCKET",
    "S3_ACCESS_KEY",
    "S3_SECRET_KEY",
    "S3_REGION",
    "S3_ENDPOINT",
    "S3_PATH_PREFIX",
    "SKILLS_CAROUSEL_BUDGET",
    "SKILLS_REEL_BUDGET",
    "SKILLS_RESEARCH_BUDGET",
    "SKILLS_SKIP_VENV",
    "SKILLS_SKIP_FFMPEG",
    "SKILLS_BATCH_PARALLELISM",
]

_GATE_FLAGS = {
    "OPENAI_SORA_API_ENABLED",
    "LYRIA_API_ENABLED",
    "SUNO_API_ENABLED",
}


def _read_value_interactive(name: str) -> str:
    if not sys.stdin.isatty():
        # Non-interactive — read line (allows piping); strip newline.
        line = sys.stdin.readline()
        return line.rstrip("\n")
    return getpass.getpass(prompt=f"  value for {name} (not echoed): ")


def _cmd_list(args: argparse.Namespace) -> int:
    entries = keysfile.read_all()
    path = keysfile.KEYS_FILE
    if not entries:
        print(f"(no keys in {path})")
        print()
        print("Add one with:  skills-keys add OPENAI_API_KEY <value>")
        return 0
    print(f"# {path}  ({len(entries)} key(s))")
    print()
    name_w = max((len(e.name) for e in entries), default=4)
    for entry in entries:
        gate = " [gate flag]" if entry.name in _GATE_FLAGS else ""
        print(f"  {entry.name:<{name_w}}  {entry.masked()}{gate}")
    print()
    print("Use 'skills-keys verify' to ping providers.")
    return 0


def _cmd_add(args: argparse.Namespace) -> int:
    name = args.name.upper()
    if name in _GATE_FLAGS and not args.value:
        # Default a gate flag to "1" when no value passed
        value = "1"
    else:
        value = args.value if args.value is not None else _read_value_interactive(name)
    if not value:
        print(f"  no value provided — aborted", file=sys.stderr)
        return 2
    try:
        new = keysfile.upsert(name, value)
    except ValueError as exc:
        print(f"  ✗ {exc}", file=sys.stderr)
        return 2
    action = "Added" if new else "Updated"
    print(f"  ✓ {action} {name} in {keysfile.KEYS_FILE}")
    if name not in _GATE_FLAGS:
        print(f"    masked: {keysfile.mask(value)}")
    print(f"    Active in new Claude Code sessions, or run: source {keysfile.KEYS_FILE}")
    return 0


def _cmd_remove(args: argparse.Namespace) -> int:
    name = args.name.upper()
    removed = keysfile.remove(name)
    if removed:
        print(f"  ✓ Removed {name} from {keysfile.KEYS_FILE}")
    else:
        print(f"  · {name} was not set — nothing to remove")
    return 0


def _cmd_enable(args: argparse.Namespace) -> int:
    name = args.name.upper()
    if name not in _GATE_FLAGS:
        print(
            f"  ! '{name}' isn't a known gate flag. Use 'add' for general keys.\n"
            f"    Known gate flags: {', '.join(sorted(_GATE_FLAGS))}",
            file=sys.stderr,
        )
        return 2
    keysfile.upsert(name, "1")
    print(f"  ✓ Enabled {name}=1 in {keysfile.KEYS_FILE}")
    return 0


def _cmd_disable(args: argparse.Namespace) -> int:
    name = args.name.upper()
    if name not in _GATE_FLAGS:
        print(
            f"  ! '{name}' isn't a known gate flag. Use 'remove' for general keys.",
            file=sys.stderr,
        )
        return 2
    removed = keysfile.remove(name)
    if removed:
        print(f"  ✓ Disabled {name} (removed)")
    else:
        print(f"  · {name} was already disabled")
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    # Load file into env so shell-unset keys still get probed
    keysfile.load_into_env(override=False)
    targets = [n.upper() for n in args.names] if args.names else verify_mod.supported_envs()
    width = max((len(n) for n in targets), default=4)
    any_invalid = False
    for env_var in targets:
        import os
        value = os.environ.get(env_var) or keysfile.get(env_var)
        result = verify_mod.verify_key(env_var, value)
        symbol = {
            "valid": "\033[32m✓\033[0m",
            "invalid": "\033[31m✗\033[0m",
            "unknown": "\033[33m?\033[0m",
            "unsupported": "\033[2m·\033[0m",
            "unset": "\033[2m–\033[0m",
        }.get(result.status, "?")
        print(f"  {symbol} {env_var:<{width}}  {result.status:<11s}  {result.detail}")
        if result.status == "invalid":
            any_invalid = True
    return 1 if any_invalid else 0


def _cmd_path(args: argparse.Namespace) -> int:
    print(str(keysfile.KEYS_FILE))
    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    lines = keysfile.export_lines(mask_values=args.mask)
    if not lines:
        print("# (no keys to export)", file=sys.stderr)
        return 0
    if args.mask:
        print("# Values masked — for inspection only. Use without --mask for eval.", file=sys.stderr)
    print("\n".join(lines))
    return 0


def _cmd_accounts(args: argparse.Namespace) -> int:
    """Social accounts live in a second store (~/.skills-tokens.json) because
    they expire and these do not. Surfaced here anyway — this is the skill
    people open when they are looking for "where do my credentials live"."""
    from .. import tokens
    from ..errors import RunnerError
    from . import auth

    # Call the command functions directly rather than rewriting sys.argv and
    # re-entering auth.main() — that left argv clobbered for anything running
    # after this in the same process.
    try:
        if args.connect:
            return auth.cmd_connect(args.connect)
        if args.revoke:
            return auth.cmd_revoke(args.revoke)
    except RunnerError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(f"# {tokens.TOKENS_FILE}")
    for line in tokens.status_lines():
        print(line)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="common.runners.cli.keys",
        description="Manage ~/.skills.env — the runner's key store.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="list keys (masked)")
    p_list.set_defaults(func=_cmd_list)

    p_add = sub.add_parser("add", help="add or update a key")
    p_add.add_argument("name")
    p_add.add_argument("value", nargs="?", default=None)
    p_add.set_defaults(func=_cmd_add)

    p_update = sub.add_parser("update", help="alias for add")
    p_update.add_argument("name")
    p_update.add_argument("value", nargs="?", default=None)
    p_update.set_defaults(func=_cmd_add)

    p_remove = sub.add_parser("remove", help="remove a key")
    p_remove.add_argument("name")
    p_remove.set_defaults(func=_cmd_remove)

    p_enable = sub.add_parser("enable", help="enable a gate flag (e.g. SUNO_API_ENABLED)")
    p_enable.add_argument("name")
    p_enable.set_defaults(func=_cmd_enable)

    p_disable = sub.add_parser("disable", help="disable a gate flag")
    p_disable.add_argument("name")
    p_disable.set_defaults(func=_cmd_disable)

    p_verify = sub.add_parser("verify", help="ping providers to validate keys")
    p_verify.add_argument("names", nargs="*", help="env vars to verify (default: all known)")
    p_verify.set_defaults(func=_cmd_verify)

    p_path = sub.add_parser("path", help="print the keys-file path")
    p_path.set_defaults(func=_cmd_path)

    p_export = sub.add_parser("export", help="print eval-ready export lines")
    p_export.add_argument("--mask", action="store_true", help="mask values (for inspection)")
    p_export.set_defaults(func=_cmd_export)

    p_accounts = sub.add_parser("accounts", help="connected social accounts (publishing)")
    p_accounts.add_argument("--connect", metavar="PLATFORM", help="run the OAuth flow for a platform")
    p_accounts.add_argument("--revoke", metavar="PLATFORM", help="forget a platform's stored token")
    p_accounts.set_defaults(func=_cmd_accounts)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
