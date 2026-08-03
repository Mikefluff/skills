# Semver comparison cheat sheet

Local and remote versions are stored as `MAJOR.MINOR.PATCH` strings (e.g. `0.1.0`, `1.12.4`).

## Comparison

Parse each version as a tuple of integers, then compare lexicographically:

```bash
ver_cmp() {
  # echoes -1 / 0 / 1 for a < b / a == b / a > b
  local a="$1" b="$2"
  IFS='.' read -r a1 a2 a3 <<<"$a"
  IFS='.' read -r b1 b2 b3 <<<"$b"
  for i in 1 2 3; do
    av=$(eval echo \$a$i); bv=$(eval echo \$b$i)
    [ "$av" -lt "$bv" ] && { echo -1; return; }
    [ "$av" -gt "$bv" ] && { echo 1; return; }
  done
  echo 0
}
```

Or in Python:

```python
def cmp(a: str, b: str) -> int:
    pa = tuple(int(x) for x in a.split("."))
    pb = tuple(int(x) for x in b.split("."))
    return (pa > pb) - (pa < pb)
```

## Pre-release / canary handling

The release pipeline in this collection does not emit pre-release suffixes (`-canary.N`, `-rc.1`, etc.). If a tag like `0.2.0-rc.1` appears, treat it as "not yet stable" and skip — only stable `X.Y.Z` tags should trigger an update offer.

## Edge cases

- **Local marker missing version field**: treat as `0.0.0` (any release is newer).
- **Remote tag without leading `v`**: strip it before comparison.
- **Equal versions**: print `up to date` and exit. Do not offer reinstall.
- **Local > remote** (user installed from main HEAD): print `local is ahead of latest release — nothing to do` and exit.
