"""A storyboard frame is keyed by what it looks like, and a paid command says what it buys and why before it asks."""

import hashlib
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import batch, spend  # noqa: E402
from common.runners.cli import _reel_spend, reel_board  # noqa: E402

FRAME = {"id": "f04", "shot": 5, "refs": ["arthur", "pit"], "shot_spec": "s", "prompt": "p", "check": "c"}


def _old_rule(frame, identity=""):
    """The hash board.json files were stamped with before 173ab80: everything but "revised", shot number included."""
    spec = {k: v for k, v in frame.items() if k != "revised"}
    return hashlib.sha256(json.dumps([spec, identity], sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]


class FrameKey(unittest.TestCase):
    def test_keys_added_at_run_time_or_by_the_editor_do_not_make_a_new_frame(self):
        busy = {**FRAME, "shot": 9, "revised": True, "_ref_names": ["Arthur"], "_assets": {"a": "a.png"},
                "jpg": "board/f04.jpg", "first_frame": "board/f04.jpg"}
        self.assertEqual(reel_board._spec_hash(FRAME, ""), reel_board._spec_hash(busy, ""))
        for key in ("prompt", "refs", "shot_spec", "check"):
            self.assertNotEqual(reel_board._spec_hash(FRAME, ""), reel_board._spec_hash({**FRAME, key: "x"}, ""))

    def test_a_board_hashed_under_the_last_rule_keeps_its_cache(self):
        last_rule = {k: v for k, v in FRAME.items() if k not in ("revised", "shot")}
        expected = hashlib.sha256(json.dumps([last_rule, ""], sort_keys=True, ensure_ascii=False).encode())
        self.assertEqual(reel_board._spec_hash(FRAME, ""), expected.hexdigest()[:12])

    def _board(self, tmp, stamp):
        out = Path(tmp, "board")
        out.mkdir()
        (out / "f04.png").write_bytes(b"png")
        (out / "board.json").write_text(json.dumps({"f04": {"score": 10, "hash": stamp}}))
        plan = Path(tmp, "plan.json")
        plan.write_text(json.dumps({"output_dir": tmp, "board": {"frames": [FRAME]}}))
        return out, plan

    def test_the_real_run_mismatch_and_its_migration(self):
        """Every hash stamped under the old rule mismatched; --mark-current re-stamps drawn frames, drawing nothing."""
        with tempfile.TemporaryDirectory() as tmp:
            out, plan = self._board(tmp, _old_rule({**FRAME, "shot": 4}))  # stamped before a shot went in ahead
            state = json.loads((out / "board.json").read_text())
            self.assertEqual(reel_board._stale([FRAME], state, set(), "", out), [(FRAME, spend.CHANGED)])
            marked = reel_board.mark_current(Namespace(plan_file=plan, only=None))
            self.assertEqual(marked, ["f04"])
            state = json.loads((out / "board.json").read_text())
            self.assertEqual(state["f04"]["score"], 10)
            self.assertEqual(reel_board._stale([FRAME], state, set(), "", out), [])
            self.assertEqual(reel_board.mark_current(Namespace(plan_file=plan, only=None)), [])

    def test_the_hash_saved_after_a_render_is_the_hash_checked_next_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            frame = dict(FRAME)
            board = {"frames": [frame], "character": "hero.png"}

            def draw(named, refs, board, png, tries):
                png.write_bytes(b"png")
                return {"score": 10}

            state = {}
            with mock.patch.object(reel_board, "_render", side_effect=draw):
                reel_board._render_all(board, [frame], state, out / "board.json", 1)
            frame["shot"] = 6  # a shot inserted before it
            self.assertEqual(reel_board._stale([frame], state, set(), "", out), [])


class Summary(unittest.TestCase):
    def test_a_short_list_is_itemised(self):
        rows = spend.format_lines([("t03a", Decimal("1.5"), spend.ASKED), ("t40", None, spend.MISSING)])
        self.assertEqual(len(rows), 2)
        self.assertIn("$1.50", rows[0])
        self.assertIn("asked (--only/--redo)", rows[0])
        self.assertIn("$?", rows[1])

    def test_a_long_list_is_counted_per_reason(self):
        lines = [(f"t{n:02d}", Decimal("0.15"), spend.MISSING) for n in range(40)] + [("t03a", Decimal("1"), spend.ASKED)]
        rows = spend.format_lines(lines)
        self.assertEqual(len(rows), 2)
        self.assertTrue(rows[0].startswith("  asked (--only/--redo): 1"))
        self.assertIn("missing: 40 ($6.00) — t00, t01, t02, t03, t04, …", rows[1])


def _item(label, index):
    return batch.BatchItem(index=index, label=label, prompt="p", kwargs={})


class Pending(unittest.TestCase):
    def _manifest(self, tmp, statuses):
        items = [_item(label, n) for n, label in enumerate(statuses, start=1)]
        for item in items:
            item.status = statuses[item.label]
        path = Path(tmp, "manifest.json")
        batch.write_manifest(path, items)
        return path

    def test_redo_buys_every_missing_shot_too_and_says_why(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._manifest(tmp, {"t01": "succeeded", "t02": "failed", "t03a": "succeeded"})
            items = [_item("t01", 1), _item("t02", 2), _item("t03a", 3), _item("t04", 4)]
            got = batch.pending_reasons(items, path, resume=True, redo=frozenset({"t03a"}))
            self.assertEqual([(i.label, why) for i, why in got],
                             [("t02", spend.FAILED), ("t03a", spend.ASKED), ("t04", spend.MISSING)])
            only = batch.pending_reasons(items, path, resume=True, redo=frozenset({"t03a"}), only=frozenset({"t03a"}))
            self.assertEqual([(i.label, why) for i, why in only], [("t03a", spend.ASKED)])
            fresh = batch.pending_reasons(items, path, resume=False)
            self.assertEqual(fresh[0][1], spend.RERUN)

    def test_reel_warns_when_redo_reaches_beyond_what_was_named(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._manifest(tmp, {"t03a": "succeeded"})
            provider = mock.Mock()
            provider.estimate_cost.return_value = Decimal("0.15")
            job = SimpleNamespace(shot_items=[_item("t03a", 1), _item("t40", 2)], manifest_path=path,
                                  video_provider=provider, music_item=None, music_provider=None,
                                  plan={}, output_dir=Path(tmp))
            lines, warnings = _reel_spend.to_buy(job, resume=False, redo=frozenset({"t03a"}), only=frozenset())
            self.assertEqual([(label, why) for label, _, why in lines], [("t03a", spend.ASKED), ("t40", spend.MISSING)])
            self.assertEqual(len(warnings), 1)
            self.assertIn("--only t03a", warnings[0])


if __name__ == "__main__":
    unittest.main()
