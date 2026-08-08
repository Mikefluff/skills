"""Guards the one table in the repo that only a human can fill in.

`docs/distribution.md` tracks where this project is listed. Nothing can verify a
directory submission offline, so the column is written by hand — and it rotted
the way hand-written columns do: the npm row said "published" while the registry
sat a release behind, because the row recorded that `make release` had been wired
to `make publish-npm`, not that an upload had happened.

What is checkable offline is the shape of the claim and the age of the review.
A status drawn from a fixed vocabulary can be compared release to release; a
free-text one cannot. A route that names a `make` target can be resolved. And a
dated marker turns "nobody has looked at this in a year" from invisible into a
failing test — the same device `test_model_registry` uses for vendor model ids.
"""

import datetime as dt
import os
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

DOC = ROOT / "docs" / "distribution.md"
MAKEFILE = ROOT / "Makefile"

# Four words, so a row can be compared against the same row a release later.
# "published, was 14 minors stale" is a sentence about history, not a status.
VOCABULARY = {"listed", "submitted", "drafted", "not submitted"}

# Long enough not to nag, short enough that a dead listing gets noticed inside a
# quarter. Vendor model ids get 120 days; a directory needs no more attention.
MAX_REVIEW_AGE_DAYS = 90


def _map_rows() -> list[list[str]]:
    """The `| Directory | Link | Route | Status |` table, minus its header."""
    rows = []
    for line in DOC.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 4 or cells[0] in {"Directory", ""} or set(cells[0]) <= {"-"}:
            continue
        rows.append(cells)
    return rows


class TestDistributionMap(unittest.TestCase):
    def test_the_table_is_found_at_all(self):
        # Every other assertion here passes vacuously against an empty list.
        self.assertGreaterEqual(len(_map_rows()), 5, "the distribution map did not parse")

    def test_every_status_comes_from_the_vocabulary(self):
        for directory, _link, _route, status in _map_rows():
            with self.subTest(directory=directory):
                self.assertIn(
                    status.strip("*` "),
                    VOCABULARY,
                    f"{directory!r} has a free-text status: {status!r}. "
                    f"Use one of {sorted(VOCABULARY)}.",
                )

    def test_every_make_route_still_exists(self):
        targets = set(re.findall(r"^([a-z][a-z0-9-]*):", MAKEFILE.read_text(encoding="utf-8"), re.M))
        for directory, _link, route, _status in _map_rows():
            for named in re.findall(r"`make ([a-z][a-z0-9-]*)`", route):
                with self.subTest(directory=directory, target=named):
                    self.assertIn(named, targets, f"route names `make {named}`, which is gone")


class TestReviewFreshness(unittest.TestCase):
    def test_the_review_date_parses(self):
        self.assertIsNotNone(self._reviewed(), "docs/distribution.md has no `Last reviewed:` date")

    def test_the_statuses_have_been_checked_recently(self):
        if os.environ.get("SKILLS_SKIP_STALENESS"):
            self.skipTest("SKILLS_SKIP_STALENESS set")
        age = (dt.date.today() - self._reviewed()).days
        self.assertLessEqual(
            age,
            MAX_REVIEW_AGE_DAYS,
            f"distribution statuses last reviewed {age} days ago. Re-check the listings "
            f"themselves, then move the date — moving it alone defeats the marker. "
            f"Set SKILLS_SKIP_STALENESS=1 to bypass for one run.",
        )

    def _reviewed(self) -> dt.date | None:
        found = re.search(r"Last reviewed:\s*(\d{4})-(\d{2})-(\d{2})", DOC.read_text(encoding="utf-8"))
        return dt.date(*map(int, found.groups())) if found else None


if __name__ == "__main__":
    unittest.main()
