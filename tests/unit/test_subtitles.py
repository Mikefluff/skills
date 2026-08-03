"""Unit tests for common/runners/subtitles.py — SRT / VTT / plain-text parsing.

These cues go straight into an ffmpeg drawtext filter with their timings, so a
parsing mistake does not raise: it burns the right words at the wrong moment,
or drops a line, and nobody notices until they watch the video.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import subtitles  # noqa: E402

SRT = """\
1
00:00:00,000 --> 00:00:02,500
First line

2
00:00:02,500 --> 00:00:05,000
Second line
continued here
"""

VTT = """\
WEBVTT

NOTE this is a comment block

cue-1
00:00:00.000 --> 00:00:02.500
<v Speaker>First <b>line</b></v>

00:00:02.500 --> 00:00:05.000
Second line
"""


class Srt(unittest.TestCase):
    def test_parses_both_cues_with_timings(self):
        cues = subtitles.parse_srt(SRT)
        self.assertEqual(len(cues), 2)
        self.assertEqual((cues[0].start, cues[0].end), (0.0, 2.5))
        self.assertEqual(cues[0].text, "First line")

    def test_multi_line_cue_is_joined_with_a_space(self):
        self.assertEqual(subtitles.parse_srt(SRT)[1].text, "Second line continued here")

    def test_index_line_is_not_mistaken_for_text(self):
        # The numeric index precedes the timecode, so the parser scans for the
        # timecode rather than assuming it is on a fixed line.
        self.assertNotIn("1", subtitles.parse_srt(SRT)[0].text)

    def test_crlf_is_handled(self):
        self.assertEqual(len(subtitles.parse_srt(SRT.replace("\n", "\r\n"))), 2)

    def test_block_without_a_timecode_is_skipped(self):
        self.assertEqual(subtitles.parse_srt("1\nnot a timecode\nsome text\n"), [])

    def test_timecode_with_no_text_is_skipped(self):
        self.assertEqual(subtitles.parse_srt("1\n00:00:00,000 --> 00:00:01,000\n"), [])

    def test_empty_input(self):
        self.assertEqual(subtitles.parse_srt(""), [])


class Vtt(unittest.TestCase):
    def test_header_and_note_blocks_are_skipped(self):
        cues = subtitles.parse_vtt(VTT)
        self.assertEqual(len(cues), 2)
        self.assertNotIn("WEBVTT", " ".join(c.text for c in cues))
        self.assertNotIn("comment", " ".join(c.text for c in cues))

    def test_inline_tags_are_stripped(self):
        # <v>/<b>/<c> would otherwise be drawn literally onto the frame.
        self.assertEqual(subtitles.parse_vtt(VTT)[0].text, "First line")

    def test_dot_millisecond_separator(self):
        self.assertEqual((subtitles.parse_vtt(VTT)[1].start,
                          subtitles.parse_vtt(VTT)[1].end), (2.5, 5.0))

    def test_cue_identifier_line_is_not_text(self):
        self.assertNotIn("cue-1", subtitles.parse_vtt(VTT)[0].text)

    def test_style_and_region_blocks_are_skipped(self):
        text = "WEBVTT\n\nSTYLE\n::cue { color: red }\n\nREGION\nid:r1\n\n00:00:00.000 --> 00:00:01.000\nHi\n"
        cues = subtitles.parse_vtt(text)
        self.assertEqual([c.text for c in cues], ["Hi"])


class ParseFile(unittest.TestCase):
    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write(self, name, body):
        p = self.dir / name
        p.write_text(body, encoding="utf-8")
        return p

    def test_extension_picks_the_parser(self):
        self.assertEqual(len(subtitles.parse_file(self.write("a.srt", SRT))), 2)
        self.assertEqual(len(subtitles.parse_file(self.write("a.vtt", VTT))), 2)

    def test_unknown_extension_sniffs_the_content(self):
        # A .txt that is really a VTT should still parse as one.
        cues = subtitles.parse_file(self.write("a.txt", VTT))
        self.assertEqual(cues[0].text, "First line")


class PlainText(unittest.TestCase):
    def test_lines_are_distributed_evenly(self):
        cues = subtitles.parse_plain_text("a\nb\nc\n", video_duration=9.0)
        self.assertEqual(len(cues), 3)
        self.assertAlmostEqual(cues[0].end, 3.0)
        self.assertAlmostEqual(cues[-1].end, 9.0)

    def test_gap_is_taken_out_of_the_cue_time_not_added_to_the_video(self):
        cues = subtitles.parse_plain_text("a\nb\n", video_duration=10.0, gap_seconds=2.0)
        self.assertAlmostEqual(cues[0].end, 4.0)
        self.assertAlmostEqual(cues[1].start, 6.0)
        self.assertLessEqual(cues[-1].end, 10.0)

    def test_gap_larger_than_the_video_falls_back_to_no_gap(self):
        cues = subtitles.parse_plain_text("a\nb\n", video_duration=1.0, gap_seconds=5.0)
        self.assertEqual(len(cues), 2)
        self.assertLessEqual(cues[-1].end, 1.0)

    def test_blank_input_and_zero_duration(self):
        self.assertEqual(subtitles.parse_plain_text("", video_duration=10.0), [])
        self.assertEqual(subtitles.parse_plain_text("a\n", video_duration=0.0), [])

    def test_cues_to_tuples_is_what_ffmpeg_wants(self):
        cues = subtitles.parse_plain_text("a\n", video_duration=2.0)
        self.assertEqual(subtitles.cues_to_tuples(cues), [(0.0, 2.0, "a")])


if __name__ == "__main__":
    unittest.main()
