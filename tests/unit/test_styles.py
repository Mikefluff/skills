"""Unit tests for common/runners/styles.py — the style library.

Every visual and audio skill resolves its look through this module, and users are
invited to add their own styles under ~/.claude/style-library/. validate_style()
is what tells them why a new file was rejected, so its output is a user-facing
contract, not an internal detail: a rule that silently stops firing turns a
broken style into a confusing render three steps later.

Frontmatter is parsed by regex rather than PyYAML (no dependency), so the small
type-coercion rules are pinned too.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import styles, styles_validate  # noqa: E402

ANCHOR_NAMES = {
    "carousel": "Style anchor (carousel)",
    "video": "Shot anchor (per-shot prompt fragment)",
    "music": "Suno Style box (paste-ready, ≤200 chars)",
}

LONG_ENOUGH = "x" * 60


# Typed defaults per modality: the required fields are not interchangeable
# strings, so a generic placeholder would trip the per-modality shape rules.
TYPED_DEFAULTS = {
    "carousel": {"text_friendly": True, "photoreal": False},
    "video": {"pacing": "medium", "dialogue_friendly": True},
    "music": {
        "bpm_range": "90-120", "energy": "calm",
        "two_box": True, "vocal_friendly": False,
    },
}


def make_body(modality, anchor_text=LONG_ENOUGH, with_anchor=True):
    """Body with every required field. The anchor goes last, in block form.

    The anchor must not also appear as an inline `**field**: value` line —
    anchor() finds the first occurrence of the marker, and an inline one runs on
    into the fields after it (see Anchor.test_inline_field_does_not_terminate).
    """
    anchor_name = ANCHOR_NAMES[modality]
    parts = [
        f"**{f}**: placeholder"
        for f in styles_validate.REQUIRED_BODY_FIELDS.get(modality, [])
        if f != anchor_name
    ]
    if with_anchor:
        parts.append(f"**{anchor_name}**:\n> {anchor_text}")
    return "\n\n".join(parts)


def make_style(modality="carousel", meta=None, body=None, stem=None):
    """A style that validates clean, so each test can break exactly one thing."""
    base = {
        "id": "test-style",
        "modality": modality,
        "display": "Test Style",
        "mood": ["calm"],
        "tags": ["editorial"],
        **TYPED_DEFAULTS.get(modality, {}),
    }
    if meta:
        base.update(meta)
        for key, value in list(meta.items()):
            if value is None:
                base.pop(key, None)

    return styles.Style(
        id=stem if stem is not None else str(base.get("id", "test-style")),
        modality=modality,
        meta=base,
        body=make_body(modality) if body is None else body,
        source_path=Path("/tmp/test-style.md"),
    )


class ValidBaseline(unittest.TestCase):
    def test_each_modality_has_a_clean_baseline(self):
        # If this fails, every other test in the file is measuring the wrong thing.
        for modality in ("carousel", "video", "music"):
            with self.subTest(modality):
                self.assertEqual(styles_validate.validate_style(make_style(modality)), [])


class Frontmatter(unittest.TestCase):
    def issues(self, **kw):
        return styles_validate.validate_style(make_style(**kw))

    def test_unknown_modality_stops_at_one_issue(self):
        style = make_style()
        style.modality = "sculpture"
        found = styles_validate.validate_style(style)
        self.assertEqual(len(found), 1)
        self.assertIn("unknown modality", found[0])

    def test_missing_required_field_is_reported_once_with_all_names(self):
        required = sorted(styles_validate.REQUIRED_FRONTMATTER["carousel"])[:2]
        found = self.issues(meta={k: None for k in required})
        missing = [i for i in found if "missing required field" in i]
        self.assertEqual(len(missing), 1)
        for name in required:
            self.assertIn(name, missing[0])

    def test_id_must_be_kebab_case(self):
        for bad in ("Test_Style", "9lives", "way-too-" + "long" * 20, ""):
            with self.subTest(bad):
                style = make_style(meta={"id": bad})
                style.id = bad
                self.assertTrue(
                    any("kebab-case" in i for i in styles_validate.validate_style(style)),
                    f"{bad!r} should have been rejected",
                )

    def test_frontmatter_id_must_match_the_filename(self):
        style = make_style(meta={"id": "other-name"}, stem="test-style")
        self.assertTrue(any("must match filename stem" in i for i in styles_validate.validate_style(style)))

    def test_modality_field_must_match_the_directory(self):
        found = self.issues(meta={"modality": "video"})
        self.assertTrue(any("must equal 'carousel'" in i for i in found))

    def test_mood_and_tags_must_be_lists_of_strings(self):
        self.assertTrue(any("must be a list" in i for i in self.issues(meta={"mood": "calm"})))
        self.assertTrue(any("must all be strings" in i for i in self.issues(meta={"tags": ["a", 3]})))

    def test_display_must_be_a_string(self):
        self.assertTrue(any("'display' must be a string" in i for i in self.issues(meta={"display": 7})))

    def test_unknown_extra_fields_are_ignored(self):
        # The frontmatter set is a floor, not a whitelist — a style may carry
        # notes the loader does not know about.
        self.assertEqual(self.issues(meta={"author": "someone", "revision": 3}), [])


class PerModalityFields(unittest.TestCase):
    def issues(self, modality, meta):
        return styles_validate.validate_style(make_style(modality, meta=meta))

    def test_carousel_booleans(self):
        for name in ("text_friendly", "photoreal"):
            with self.subTest(name):
                found = self.issues("carousel", {name: "yes"})
                self.assertTrue(any("true/false" in i for i in found))
                self.assertEqual(self.issues("carousel", {name: True}), [])

    def test_video_pacing_is_a_closed_set(self):
        self.assertTrue(any("'pacing' must be one of" in i for i in self.issues("video", {"pacing": "brisk"})))
        for good in styles_validate._VALID_PACING:
            with self.subTest(good):
                self.assertEqual(self.issues("video", {"pacing": good}), [])

    def test_video_dialogue_friendly_is_boolean(self):
        self.assertTrue(any("dialogue_friendly" in i for i in self.issues("video", {"dialogue_friendly": "y"})))

    def test_music_bpm_range_shape(self):
        for bad in ("120", "120bpm", "1200-1300", 120):
            with self.subTest(bad):
                self.assertTrue(any("bpm_range" in i for i in self.issues("music", {"bpm_range": bad})))
        self.assertEqual(self.issues("music", {"bpm_range": "90-120"}), [])

    def test_music_energy_is_a_closed_set(self):
        self.assertTrue(any("'energy' must be one of" in i for i in self.issues("music", {"energy": "loud"})))
        for good in styles_validate._VALID_ENERGY:
            with self.subTest(good):
                self.assertEqual(self.issues("music", {"energy": good}), [])

    def test_a_carousel_only_rule_does_not_fire_on_video(self):
        # text_friendly is meaningless for video; a shared validator would leak.
        self.assertEqual(self.issues("video", {"text_friendly": "not-a-bool"}), [])


class Body(unittest.TestCase):
    def test_missing_body_field_is_reported(self):
        fields = [f for f in styles_validate.REQUIRED_BODY_FIELDS["carousel"]
                  if f != ANCHOR_NAMES["carousel"]]
        style = make_style(body=f"**{ANCHOR_NAMES['carousel']}**:\n> {LONG_ENOUGH}")
        found = styles_validate.validate_style(style)
        self.assertTrue(any(f"body missing field: '{fields[0]}'" in i for i in found))

    def test_short_anchor_is_rejected(self):
        # An anchor is injected into every prompt; a stub one silently produces
        # styleless output rather than an error.
        found = styles_validate.validate_style(make_style(body=make_body("carousel", "too short")))
        self.assertTrue(any("too short" in i for i in found))

    def test_absent_anchor_is_rejected(self):
        found = styles_validate.validate_style(make_style(body=make_body("carousel", with_anchor=False)))
        self.assertTrue(any("empty or too short" in i for i in found))


class Anchor(unittest.TestCase):
    def anchor_of(self, body, name="A"):
        return styles.Style("s", "carousel", {}, body, Path("/tmp/s.md")).anchor(name)

    def test_absent_marker_returns_none(self):
        self.assertIsNone(self.anchor_of("**B**: text"))

    def test_blockquote_markers_are_stripped_and_lines_joined(self):
        self.assertEqual(self.anchor_of("**A**:\n> one\n> two\n"), "one two")

    def test_stops_at_the_next_field(self):
        self.assertEqual(self.anchor_of("**A**:\n> mine\n\n**B**:\n> theirs\n"), "mine")

    def test_stops_at_the_next_heading(self):
        self.assertEqual(self.anchor_of("**A**:\n> mine\n\n## Section\n\nother\n"), "mine")

    def test_empty_anchor_returns_none_not_empty_string(self):
        # None and "" mean different things to the caller: absent vs blank.
        self.assertIsNone(self.anchor_of("**A**:\n\n**B**:\n> x"))

    def test_inline_field_does_not_terminate_the_anchor(self):
        # Current behaviour, pinned rather than endorsed: the walk stops at a
        # line that starts with ** AND ends with ":", so a field written inline
        # as `**B**: value` is swallowed into the anchor above it. Every shipped
        # style writes the field after an anchor in block form, so nothing is
        # affected today — but a user-authored style could be.
        self.assertEqual(self.anchor_of("**A**:\n> mine\n\n**B**: theirs\n"), "mine **B**: theirs")


class ParseValue(unittest.TestCase):
    def parse(self, raw):
        return styles._parse_value(raw)

    def test_blank_is_empty_string(self):
        self.assertEqual(self.parse("   "), "")

    def test_quotes_are_stripped(self):
        self.assertEqual(self.parse('"hello"'), "hello")
        self.assertEqual(self.parse("'hello'"), "hello")

    def test_inline_list(self):
        self.assertEqual(self.parse("[a, b, c]"), ["a", "b", "c"])
        self.assertEqual(self.parse("[]"), [])
        self.assertEqual(self.parse('["a b", c]'), ["a b", "c"])

    def test_booleans_both_spellings(self):
        for raw in ("true", "TRUE", "yes"):
            self.assertIs(self.parse(raw), True)
        for raw in ("false", "No"):
            self.assertIs(self.parse(raw), False)

    def test_numbers(self):
        self.assertEqual(self.parse("42"), 42)
        self.assertEqual(self.parse("-7"), -7)
        self.assertEqual(self.parse("1.5"), 1.5)

    def test_bare_text_is_left_alone(self):
        # "90-120" must stay a string — it is a bpm_range, not arithmetic.
        self.assertEqual(self.parse("90-120"), "90-120")
        self.assertEqual(self.parse("deep teal"), "deep teal")


class ShippedLibrary(unittest.TestCase):
    """The bundled styles must pass their own validator."""

    def test_every_bundled_style_validates(self):
        found_any = False
        for modality in ("carousel", "video", "music"):
            for style in styles.list_styles(modality):
                found_any = True
                with self.subTest(f"{modality}/{style.id}"):
                    self.assertEqual(styles_validate.validate_style(style), [])
        self.assertTrue(found_any, "no bundled styles were discovered")


if __name__ == "__main__":
    unittest.main()
