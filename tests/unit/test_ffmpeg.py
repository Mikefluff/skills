"""Unit tests for common/runners/ffmpeg.py — the argv it hands to subprocess.

An ffmpeg filter graph is a string, and a wrong one does not raise: it produces
a video with the music at the wrong level, or captions a second out of step, or
a GIF that bands. Nobody notices until they watch the output. So the commands
are pinned here rather than trusted.

Nothing is executed — subprocess.run is patched and the argv is inspected.
"""

import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import ffmpeg  # noqa: E402

VIDEO = Path("/tmp/in.mp4")
AUDIO = Path("/tmp/music.mp3")


class FfmpegCase(unittest.TestCase):
    def setUp(self):
        self._run = mock.patch.object(subprocess, "run").start()
        self._mkdir = mock.patch.object(Path, "mkdir").start()
        self.addCleanup(mock.patch.stopall)

    def calls(self):
        return [c.args[0] for c in self._run.call_args_list]

    def flag(self, cmd, name):
        """The value following a flag, e.g. flag(cmd, '-af')."""
        return cmd[cmd.index(name) + 1]


class MusicFilter(unittest.TestCase):
    def test_volume_only_by_default_when_no_fades(self):
        opts = ffmpeg.MixOptions(audio_volume=0.5, fade_in=0.0, fade_out=0.0)
        self.assertEqual(opts.music_filter(), "volume=0.5")

    def test_fade_out_is_on_by_default(self):
        self.assertEqual(
            ffmpeg.MixOptions().music_filter(),
            "volume=0.8,afade=t=out:st=0:d=0.5",
        )

    def test_both_fades_in_order(self):
        opts = ffmpeg.MixOptions(audio_volume=1.0, fade_in=2.0, fade_out=3.0)
        self.assertEqual(
            opts.music_filter(),
            "volume=1.0,afade=t=in:st=0:d=2.0,afade=t=out:st=0:d=3.0",
        )


class MixModes(FfmpegCase):
    def test_replace_maps_the_music_as_the_only_audio(self):
        ffmpeg.mix_audio_with_modes(VIDEO, AUDIO, Path("/tmp/out.mp4"))
        cmd = self.calls()[0]
        self.assertEqual(self.flag(cmd, "-af"), "volume=0.8,afade=t=out:st=0:d=0.5")
        # 0:v from the video, 1:a from the music file — the original audio is dropped.
        self.assertEqual([cmd[i + 1] for i, a in enumerate(cmd) if a == "-map"], ["0:v", "1:a"])
        self.assertNotIn("-filter_complex", cmd)

    def test_overlay_mixes_both_tracks(self):
        ffmpeg.mix_audio_with_modes(
            VIDEO, AUDIO, Path("/tmp/out.mp4"), ffmpeg.MixOptions(mode="overlay")
        )
        graph = self.flag(self.calls()[0], "-filter_complex")
        self.assertIn("[0:a][music]amix=inputs=2", graph)
        self.assertNotIn("sidechaincompress", graph)

    def test_duck_sidechains_music_under_the_original(self):
        ffmpeg.mix_audio_with_modes(
            VIDEO, AUDIO, Path("/tmp/out.mp4"),
            ffmpeg.MixOptions(mode="duck", duck_amount=0.3),
        )
        graph = self.flag(self.calls()[0], "-filter_complex")
        # The original audio is the sidechain key; the music is what gets ducked.
        self.assertIn("[music][0:a]sidechaincompress=", graph)
        self.assertIn("weights=1.0 0.3", graph)

    def test_unknown_mode_is_rejected_before_running_anything(self):
        with self.assertRaises(ValueError):
            ffmpeg.mix_audio_with_modes(
                VIDEO, AUDIO, Path("/tmp/out.mp4"), ffmpeg.MixOptions(mode="sidechain")
            )
        self._run.assert_not_called()

    def test_mix_audio_over_video_is_replace_regardless_of_the_mode_passed(self):
        # The thin wrapper predates modes and its contract is "replace".
        ffmpeg.mix_audio_over_video(
            VIDEO, AUDIO, Path("/tmp/out.mp4"), ffmpeg.MixOptions(mode="duck")
        )
        cmd = self.calls()[0]
        self.assertNotIn("-filter_complex", cmd)
        self.assertEqual(self.flag(cmd, "-af"), "volume=0.8,afade=t=out:st=0:d=0.5")


class Captions(FfmpegCase):
    CUES = [(0.0, 1.5, "hello"), (1.5, 3.0, "world")]

    def test_one_drawtext_per_cue_gated_to_its_window(self):
        ffmpeg.burn_captions(VIDEO, self.CUES, Path("/tmp/out.mp4"))
        vf = self.flag(self.calls()[0], "-vf")
        self.assertEqual(vf.count("drawtext="), 2)
        self.assertIn("enable='between(t,0.00,1.50)'", vf)
        self.assertIn("enable='between(t,1.50,3.00)'", vf)

    def test_style_reaches_the_filter(self):
        ffmpeg.burn_captions(
            VIDEO, self.CUES, Path("/tmp/out.mp4"),
            ffmpeg.CaptionStyle(font_size=72, font_color="yellow", box_color="red@0.9"),
        )
        vf = self.flag(self.calls()[0], "-vf")
        self.assertIn("fontsize=72", vf)
        self.assertIn("fontcolor=yellow", vf)
        self.assertIn("boxcolor=red@0.9", vf)

    def test_filter_metacharacters_are_escaped(self):
        # A colon or comma in caption text would otherwise terminate the filter
        # argument and ffmpeg would reject the whole command.
        ffmpeg.burn_captions(VIDEO, [(0.0, 1.0, "10:30, sharp")], Path("/tmp/out.mp4"))
        vf = self.flag(self.calls()[0], "-vf")
        self.assertIn(r"10\:30\, sharp", vf)

    def test_apostrophes_become_typographic_rather_than_breaking_the_quote(self):
        ffmpeg.burn_captions(VIDEO, [(0.0, 1.0, "don't")], Path("/tmp/out.mp4"))
        self.assertIn("don’t", self.flag(self.calls()[0], "-vf"))

    def test_no_captions_stream_copies_instead_of_failing(self):
        ffmpeg.burn_captions(VIDEO, [], Path("/tmp/out.mp4"))
        cmd = self.calls()[0]
        self.assertIn("-c", cmd)
        self.assertNotIn("-vf", cmd)


class Gif(FfmpegCase):
    def test_two_passes_palettegen_then_paletteuse(self):
        ffmpeg.mp4_to_gif(VIDEO, Path("/tmp/out.gif"))
        first, second = self.calls()
        self.assertIn("palettegen=max_colors=256:stats_mode=diff", self.flag(first, "-vf"))
        self.assertIn("paletteuse=dither=bayer", self.flag(second, "-filter_complex"))

    def test_palette_is_removed_after_the_second_pass(self):
        with mock.patch.object(Path, "unlink") as unlink:
            ffmpeg.mp4_to_gif(VIDEO, Path("/tmp/out.gif"))
        unlink.assert_called_once()

    def test_width_adds_a_lanczos_scale_and_none_does_not(self):
        self.assertEqual(
            ffmpeg.GifOptions(fps=15, width=480).scale_filter(),
            "fps=15,scale=480:-1:flags=lanczos",
        )
        self.assertEqual(ffmpeg.GifOptions(fps=15).scale_filter(), "fps=15")

    def test_trim_window(self):
        self.assertEqual(
            ffmpeg.GifOptions(start=1.5, duration=2.0).trim_args(),
            ["-ss", "1.500", "-t", "2.000"],
        )
        self.assertEqual(ffmpeg.GifOptions().trim_args(), [])

    def test_trim_is_applied_to_both_passes(self):
        # Trimming only the palette pass would build the palette from a
        # different set of frames than the ones being encoded.
        ffmpeg.mp4_to_gif(VIDEO, Path("/tmp/out.gif"), ffmpeg.GifOptions(start=2.0))
        for cmd in self.calls():
            self.assertIn("-ss", cmd)

    def test_loop_is_infinite_by_default(self):
        ffmpeg.mp4_to_gif(VIDEO, Path("/tmp/out.gif"))
        self.assertEqual(self.flag(self.calls()[1], "-loop"), "0")


class Concat(FfmpegCase):
    def test_fewer_than_two_shots_is_rejected(self):
        with self.assertRaises(ValueError):
            ffmpeg.concat_videos([VIDEO], Path("/tmp/out.mp4"))
        self._run.assert_not_called()

    def test_uses_the_concat_demuxer_without_re_encoding(self):
        with mock.patch.object(Path, "write_text"), mock.patch.object(Path, "resolve", lambda self: self):
            ffmpeg.concat_videos([VIDEO, AUDIO], Path("/tmp/out.mp4"))
        cmd = self.calls()[0]
        self.assertEqual(self.flag(cmd, "-f"), "concat")
        self.assertEqual(self.flag(cmd, "-c"), "copy")


if __name__ == "__main__":
    unittest.main()
