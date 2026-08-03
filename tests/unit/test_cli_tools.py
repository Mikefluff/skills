"""Characterisation tests for the single-call tool CLIs.

bg, upscale, stylize, transcribe, subtitle and the four generic dispatch CLIs
(image / video / music / audio) are the half of common/runners/cli/ that is not
plan-driven. Gate 14 proves they import. It does not execute a single line of
main(), which is how a signature change to output.save() reached two of them
without anything going red.

So the exit codes are pinned, and — deliberately — the success paths too, since
that is where a stale call site hides: every one of these ends by writing a file
through output.save(), and a TypeError there is invisible until a user runs it
with a working key.

No network: providers are faked and ffmpeg is patched out.
"""

import argparse
import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import config, ffmpeg as ff_mod  # noqa: E402
from common.runners.errors import KeyMissingError, ProviderError  # noqa: E402
from common.runners.providers.base import GenerationResult, JobHandle, Provider  # noqa: E402

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32


class FakeProvider(Provider):
    modality = "image"

    def __init__(self, name="replicate-image", available=True, async_job=False, fail=None):
        self.name = name
        self.requires_env = () if available else ("SOME_KEY",)
        self._async = async_job
        self._fail = fail
        self.seen_kwargs = None

    def generate(self, prompt, **kwargs):
        self.seen_kwargs = kwargs
        if self._fail:
            raise self._fail
        if self._async:
            return JobHandle(provider=self.name, job_id="j1", started_at=0.0)
        return GenerationResult(content=PNG, mime="image/png", extension="png")

    def poll(self, handle, timeout=600.0):
        return GenerationResult(content=PNG, mime="image/png", extension="png")


def invoke(module_name, argv_tail, provider=None):
    """Run a tool CLI's main() in-process. Returns (exit_code, stdout, stderr)."""
    import importlib

    module = importlib.import_module(f"common.runners.cli.{module_name}")
    argv = [f"common.runners.cli.{module_name}", *argv_tail]
    out, err = io.StringIO(), io.StringIO()

    getter = config.get_provider if provider is None else (lambda _name: provider)
    with mock.patch.object(sys, "argv", argv), \
            mock.patch.object(config, "get_provider", side_effect=getter), \
            mock.patch.object(config, "load_all_providers"), \
            mock.patch("common.runners.output.s3_configured", return_value=False), \
            redirect_stdout(out), redirect_stderr(err):
        code = module.main()
    return code, out.getvalue(), err.getvalue()


class ToolCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        # Every tool defaults to ./generated/... — keep the repo clean.
        self._cwd = mock.patch.object(Path, "cwd", return_value=self.dir).start()
        self.addCleanup(mock.patch.stopall)

    def out_file(self, name="out.png"):
        return self.dir / name


# ── the Replicate one-shot tools: bg, upscale, stylize ──────────────────────

REPLICATE_TOOLS = ("bg", "upscale", "stylize")


class ReplicateTools(ToolCase):
    def test_check_reports_missing_env_as_two(self):
        for name in REPLICATE_TOOLS:
            with self.subTest(name):
                code, _out, err = invoke(
                    name, ["--image", "a.png", "--check"], FakeProvider(available=False)
                )
                self.assertEqual(code, 2)
                self.assertIn("missing env", err)

    def test_check_succeeds_when_configured(self):
        for name in REPLICATE_TOOLS:
            with self.subTest(name):
                code, out, _err = invoke(
                    name, ["--image", "a.png", "--check"], FakeProvider()
                )
                self.assertEqual(code, 0)
                self.assertIn("OK", out)

    def test_cost_only_never_calls_the_provider(self):
        for name in REPLICATE_TOOLS:
            with self.subTest(name):
                provider = FakeProvider()
                code, out, _err = invoke(name, ["--image", "a.png", "--cost-only"], provider)
                self.assertEqual(code, 0)
                self.assertIn("estimated cost", out)
                self.assertIsNone(provider.seen_kwargs)

    def test_missing_env_without_check_is_two(self):
        for name in REPLICATE_TOOLS:
            with self.subTest(name):
                code, _out, err = invoke(
                    name, ["--image", "a.png"], FakeProvider(available=False)
                )
                self.assertEqual(code, 2)
                self.assertIn("missing env", err)

    def test_unknown_provider_slug_is_two(self):
        def boom(_name):
            raise KeyError("unknown provider 'nope'")

        for name in REPLICATE_TOOLS:
            with self.subTest(name):
                with mock.patch.object(config, "get_provider", side_effect=boom):
                    code, _out, _err = invoke(name, ["--image", "a.png"], provider=None)
                self.assertEqual(code, 2)

    def test_writes_to_explicit_output_and_prints_the_path(self):
        for name in REPLICATE_TOOLS:
            with self.subTest(name):
                dest = self.out_file(f"{name}.png")
                code, out, _err = invoke(
                    name, ["--image", "a.png", "--output", str(dest)], FakeProvider()
                )
                self.assertEqual(code, 0)
                self.assertEqual(dest.read_bytes(), PNG)
                self.assertEqual(out.strip(), str(dest))

    def test_default_output_path_goes_through_output_save(self):
        # The regression this file exists for: output.save() changed shape and
        # two call sites kept the old keywords. Only the default-path branch
        # touches it, so --output would not have caught it.
        for name in REPLICATE_TOOLS:
            with self.subTest(name):
                target = self.dir / "generated" / name
                with mock.patch("common.runners.output.write_local") as write:
                    code, out, _err = invoke(
                        name, ["--image", str(self.dir / "photo.jpg")], FakeProvider()
                    )
                self.assertEqual(code, 0)
                write.assert_called_once()
                self.assertEqual(write.call_args.args[0], PNG)
                self.assertTrue(out.strip(), "the saved path must reach stdout")
                del target

    def test_async_job_is_polled(self):
        for name in REPLICATE_TOOLS:
            with self.subTest(name):
                dest = self.out_file(f"{name}-async.png")
                code, _out, _err = invoke(
                    name, ["--image", "a.png", "--output", str(dest)],
                    FakeProvider(async_job=True),
                )
                self.assertEqual(code, 0)
                self.assertEqual(dest.read_bytes(), PNG)

    def test_missing_key_at_call_time_is_two_and_provider_error_is_five(self):
        cases = ((KeyMissingError("x", ["K"]), 2), (ProviderError("x", 500, "boom"), 5))
        for exc, expected in cases:
            for name in REPLICATE_TOOLS:
                with self.subTest(f"{name}-{expected}"):
                    code, _out, _err = invoke(
                        name, ["--image", "a.png"], FakeProvider(fail=exc)
                    )
                    self.assertEqual(code, expected)


class StylizeSpecifics(ToolCase):
    def test_custom_style_without_prompt_mod_is_two(self):
        code, _out, err = invoke(
            "stylize", ["--image", "a.png", "--style", "custom"], FakeProvider()
        )
        self.assertEqual(code, 2)
        self.assertIn("--prompt-mod", err)

    def test_unknown_style_is_two(self):
        code, _out, err = invoke(
            "stylize", ["--image", "a.png", "--style", "hologram"], FakeProvider()
        )
        self.assertEqual(code, 2)
        self.assertIn("unknown --style", err)

    def test_gpt_image_2_is_refused_with_a_pointer(self):
        # The edits endpoint is not wired up; failing early beats a vendor 400.
        code, _out, err = invoke(
            "stylize", ["--image", "a.png", "--model", "gpt-image-2"],
            FakeProvider(name="gpt-image-2"),
        )
        self.assertEqual(code, 2)
        self.assertIn("flux-kontext", err)

    def test_image_reference_uses_the_kwarg_each_provider_expects(self):
        cases = {
            "flux-kontext": "input_image",
            "nano-banana-pro": "image_url",
            "replicate-image": "image",
        }
        for model, expected_key in cases.items():
            with self.subTest(model):
                provider = FakeProvider(name=model)
                invoke(
                    "stylize",
                    ["--image", "a.png", "--model", model, "--output", str(self.out_file())],
                    provider,
                )
                self.assertIn(expected_key, provider.seen_kwargs)


class Transcribe(ToolCase):
    def media(self, name="clip.mp4"):
        p = self.dir / name
        p.write_bytes(b"\x00" * 64)
        return p

    def test_missing_input_file_is_two(self):
        code, _out, err = invoke(
            "transcribe", ["--input", str(self.dir / "nope.mp4")], FakeProvider(name="whisper-1")
        )
        self.assertEqual(code, 2)
        self.assertIn("not found", err)

    def test_cost_only_without_ffprobe_still_exits_zero(self):
        with mock.patch.object(ff_mod, "get_duration", return_value=None):
            code, out, _err = invoke(
                "transcribe", ["--input", str(self.media()), "--cost-only"],
                FakeProvider(name="whisper-1"),
            )
        self.assertEqual(code, 0)
        self.assertIn("estimated cost", out)

    def test_cost_only_with_duration_reports_minutes(self):
        with mock.patch.object(ff_mod, "get_duration", return_value=120.0):
            code, out, _err = invoke(
                "transcribe", ["--input", str(self.media()), "--cost-only"],
                FakeProvider(name="whisper-1"),
            )
        self.assertEqual(code, 0)
        self.assertIn("2.00min", out)

    def test_transcript_is_written_next_to_the_input_by_default(self):
        media = self.media()
        with mock.patch.object(ff_mod, "get_duration", return_value=10.0):
            code, out, _err = invoke(
                "transcribe", ["--input", str(media)], FakeProvider(name="whisper-1")
            )
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), str(media.with_suffix(".srt")))
        self.assertTrue(media.with_suffix(".srt").is_file())

    def test_format_picks_the_extension(self):
        media = self.media()
        with mock.patch.object(ff_mod, "get_duration", return_value=10.0):
            invoke(
                "transcribe", ["--input", str(media), "--format", "text"],
                FakeProvider(name="whisper-1"),
            )
        self.assertTrue(media.with_suffix(".txt").is_file())


class Subtitle(ToolCase):
    def video(self):
        p = self.dir / "clip.mp4"
        p.write_bytes(b"\x00" * 64)
        return p

    def burn(self, tail, found=True):
        # `video` is positional on the burn subcommand.
        probe = ff_mod.FfmpegProbe(found=found, binary="ffmpeg" if found else None)
        with mock.patch.object(ff_mod, "detect_ffmpeg", return_value=probe), \
                mock.patch.object(subprocess, "run"):
            return invoke("subtitle", ["burn", *tail])

    def test_missing_video_is_two(self):
        code, _out, err = self.burn([str(self.dir / "nope.mp4"), "--inline", "hi"])
        self.assertEqual(code, 2)
        self.assertIn("not found", err)

    def test_no_subtitle_source_is_rejected_by_the_parser(self):
        # --subtitle / --inline are a required mutually-exclusive group, so this
        # never reaches _cmd_burn. Its own "provide --subtitle or --inline"
        # branch is therefore unreachable.
        with self.assertRaises(SystemExit) as caught:
            self.burn([str(self.video())])
        self.assertEqual(caught.exception.code, 2)

    def test_missing_subtitle_file_is_two(self):
        code, _out, _err = self.burn(
            [str(self.video()), "--subtitle", str(self.dir / "none.srt")]
        )
        self.assertEqual(code, 2)

    def test_absent_ffmpeg_is_two(self):
        code, _out, err = self.burn(
            [str(self.video()), "--inline", "hello"], found=False
        )
        self.assertEqual(code, 2)
        self.assertIn("ffmpeg not found", err)

    def test_inline_caption_burns_and_prints_the_output(self):
        video = self.video()
        with mock.patch.object(ff_mod, "get_duration", return_value=8.0):
            code, out, _err = self.burn([str(video), "--inline", "hello"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), str(video.with_name("clip-subtitled.mp4")))

    def test_plain_text_without_a_probeable_duration_is_two(self):
        # Distributing cues evenly needs a duration; guessing would desync them.
        txt = self.dir / "lines.txt"
        txt.write_text("one\ntwo\n", encoding="utf-8")
        with mock.patch.object(ff_mod, "get_duration", return_value=None):
            code, _out, err = self.burn([str(self.video()), "--subtitle", str(txt)])
        self.assertEqual(code, 2)
        self.assertIn("duration", err)


class SharedDispatch(ToolCase):
    """cli/_shared.py backs the image / video / music / audio entry points."""

    def dispatch(self, tail, provider=None):
        return invoke("image", tail, provider)

    def test_list_providers_exits_zero(self):
        # Needs the real registry, so let load_all_providers actually run.
        config.load_all_providers()
        with mock.patch.object(sys, "argv", ["image", "--list-providers"]):
            out = io.StringIO()
            with redirect_stdout(out):
                from common.runners.cli import image

                code = image.main()
        self.assertEqual(code, 0)
        self.assertIn("Image providers:", out.getvalue())

    def test_missing_model_is_a_parser_error(self):
        with self.assertRaises(SystemExit) as caught:
            self.dispatch(["--prompt", "a cat"])
        self.assertEqual(caught.exception.code, 2)

    def test_wrong_modality_is_two(self):
        provider = FakeProvider(name="veo-3-1")
        provider.modality = "video"
        code, _out, err = self.dispatch(["--model", "veo-3-1", "--prompt", "x"], provider)
        self.assertEqual(code, 2)
        self.assertIn("not image", err)

    def test_cost_only_exits_zero(self):
        code, out, _err = self.dispatch(
            ["--model", "fake", "--prompt", "x", "--cost-only"], FakeProvider(name="fake")
        )
        self.assertEqual(code, 0)
        self.assertIn("estimated cost", out)

    def test_missing_key_falls_back_to_saving_the_prompt(self):
        # Exit 4 means "we did not spend anything, but your prompt is on disk".
        # It is the only path that calls save_prompt_only, and it was broken by
        # a signature change that nothing executed.
        provider = FakeProvider(name="fake", available=False)
        code, out, _err = self.dispatch(
            ["--model", "fake", "--prompt", "a cat", "--output", str(self.dir)], provider
        )
        self.assertEqual(code, 4)
        saved = list(self.dir.glob("*.txt"))
        self.assertEqual(len(saved), 1)
        self.assertIn("a cat", saved[0].read_text(encoding="utf-8"))
        self.assertTrue(out.strip())

    def test_provider_failure_also_saves_the_prompt_and_exits_five(self):
        provider = FakeProvider(name="fake", fail=ProviderError("fake", 500, "boom"))
        code, _out, _err = self.dispatch(
            ["--model", "fake", "--prompt", "a cat", "--output", str(self.dir)], provider
        )
        self.assertEqual(code, 5)
        self.assertEqual(len(list(self.dir.glob("*.txt"))), 1)

    def test_success_writes_the_asset(self):
        code, out, _err = self.dispatch(
            ["--model", "fake", "--prompt", "a cat", "--output", str(self.dir), "--yes"],
            FakeProvider(name="fake"),
        )
        self.assertEqual(code, 0)
        self.assertEqual(len(list(self.dir.glob("*.png"))), 1)
        self.assertTrue(out.strip())


class GatherKwargs(unittest.TestCase):
    """The passthrough table between argparse and provider.generate()."""

    def args(self, **over):
        base = dict(
            variants=1, duration=None, lyrics=None, lyrics_file=None, instrumental=False,
            image_url=None, video_url=None, size=None, quality=None, voice=None,
            voice_id=None, speed=None, lang=None, fal_model=None, replicate_model=None,
        )
        base.update(over)
        return argparse.Namespace(**base)

    def gather(self, **over):
        from common.runners.cli import _shared

        return _shared.gather_kwargs(self.args(**over))

    def test_variants_is_always_present(self):
        self.assertEqual(self.gather()["variants"], 1)

    def test_nothing_else_is_passed_when_nothing_was_asked_for(self):
        # A provider receiving size=None would forward it to the vendor as a
        # literal null and get a 400 back.
        self.assertEqual(set(self.gather()), {"variants"})

    def test_duration_feeds_both_seconds_and_minutes(self):
        # One --duration flag serves video (seconds) and music (minutes); each
        # provider reads the one it understands.
        got = self.gather(duration=8.0)
        self.assertEqual(got["duration_seconds"], 8.0)
        self.assertEqual(got["duration_minutes"], 8.0)

    def test_lyrics_file_is_read_only_when_lyrics_is_absent(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write("from file")
            path = Path(fh.name)
        self.addCleanup(path.unlink)
        self.assertEqual(self.gather(lyrics_file=path)["lyrics"], "from file")
        self.assertEqual(self.gather(lyrics="inline", lyrics_file=path)["lyrics"], "inline")

    def test_speed_zero_survives(self):
        # Guarded on `is not None`, not truthiness — 0.0 is a legal speed.
        self.assertEqual(self.gather(speed=0.0)["speed"], 0.0)

    def test_passthrough_values_reach_the_provider(self):
        got = self.gather(size="1024x1024", quality="high", voice_id="v1", lang="ru")
        self.assertEqual(got["size"], "1024x1024")
        self.assertEqual(got["quality"], "high")
        self.assertEqual(got["voice_id"], "v1")
        self.assertEqual(got["lang"], "ru")

    def test_instrumental_only_appears_when_set(self):
        self.assertNotIn("instrumental", self.gather())
        self.assertIs(self.gather(instrumental=True)["instrumental"], True)


if __name__ == "__main__":
    unittest.main()
