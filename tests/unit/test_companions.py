"""Extra files a single call produced reach disk, the manifest, and resume.

One model in the collection returns a set rather than a file: Seedream's
`layerize` decomposes an image into 2-17 transparent PNGs and bills $0.03375 for
each. Everything downstream of a provider was written when one call meant one
file — `output.save`, `BatchItem.output_path`, the resume check that decides
whether to buy an item again.

`companions` is a suffix rather than a rewrite, so the interesting cases are the
boring ones: a provider that returns nothing extra must behave exactly as before,
and a resumed batch must not re-purchase seventeen layers to recover a filename
it already had.
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.runners import batch as batch_mod  # noqa: E402
from common.runners import output as output_mod  # noqa: E402
from common.runners.providers.base import Companion, GenerationResult, Provider  # noqa: E402

PNG = b"\x89PNG\r\n\x1a\n"


def layered(n=3):
    return GenerationResult(
        content=PNG + b"bg",
        mime="image/png",
        extension="png",
        companions=tuple(
            Companion(content=PNG + name.encode(), mime="image/png", extension="png", name=name)
            for name in ("subject", "title", "logo")[: n - 1]
        ),
    )


class LayerProvider(Provider):
    modality = "image"
    name = "layer-fake"
    requires_env: tuple[str, ...] = ()

    def __init__(self, layers=3):
        self.calls = 0
        self._layers = layers

    def estimate_cost(self, **kwargs):
        return None

    def generate(self, prompt, **kwargs):
        self.calls += 1
        return layered(self._layers)


class Case(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        patch = mock.patch.object(output_mod, "s3_configured", return_value=False)
        patch.start()
        self.addCleanup(patch.stop)


class TestSaveResult(Case):
    def opts(self, slug="poster"):
        return output_mod.SaveOptions(slug=slug, output_dir=self.dir)

    def test_a_plain_result_saves_exactly_one_file(self):
        plain = GenerationResult(content=PNG, mime="image/png", extension="png")
        primary, companions = output_mod.save_result(plain, "image", "png", self.opts())
        self.assertEqual([], companions)
        self.assertTrue(primary.local_path.is_file())
        self.assertEqual(1, len(list(self.dir.iterdir())))

    def test_every_companion_lands_beside_the_primary(self):
        primary, companions = output_mod.save_result(layered(3), "image", "png", self.opts())
        self.assertEqual(2, len(companions))
        self.assertEqual(3, len(list(self.dir.iterdir())))
        self.assertEqual(primary.local_path.parent, companions[0].local_path.parent)

    def test_filenames_carry_the_layer_name_and_its_order(self):
        # `-01.png` through `-17.png` is not a layer set, it is a puzzle.
        _, companions = output_mod.save_result(layered(3), "image", "png", self.opts())
        names = [c.local_path.name for c in companions]
        self.assertTrue(any("01-subject" in n for n in names), names)
        self.assertTrue(any("02-title" in n for n in names), names)

    def test_an_unnamed_companion_still_gets_a_stable_filename(self):
        result = GenerationResult(
            content=PNG, mime="image/png", extension="png",
            companions=(Companion(content=PNG, mime="image/png", extension="png"),),
        )
        _, companions = output_mod.save_result(result, "image", "png", self.opts())
        self.assertIn("01-layer", companions[0].local_path.name)

    def test_companion_content_is_its_own(self):
        _, companions = output_mod.save_result(layered(3), "image", "png", self.opts())
        self.assertEqual(PNG + b"subject", companions[0].local_path.read_bytes())


class TestBatch(Case):
    def spec(self, *, resume=False):
        return batch_mod.BatchSpec(
            modality="image",
            output_dir=self.dir / "out",
            manifest_path=self.dir / "manifest.json",
            parallelism=1,
            resume=resume,
        )

    def items(self, n=2):
        return [
            batch_mod.BatchItem(index=i, label=f"slide-{i}", prompt=f"p-{i}") for i in range(n)
        ]

    def test_the_manifest_records_what_was_billed_for(self):
        result = batch_mod.run_batch(LayerProvider(3), self.items(2), self.spec())
        for item in result.items:
            self.assertEqual(2, len(item.companion_paths))
            for path in item.companion_paths:
                self.assertTrue(Path(path).is_file())

    def test_resume_does_not_re_purchase_a_layer_set(self):
        provider = LayerProvider(3)
        first = batch_mod.run_batch(provider, self.items(2), self.spec())
        self.assertEqual(2, provider.calls)

        again = batch_mod.run_batch(provider, self.items(2), self.spec(resume=True))
        self.assertEqual(2, provider.calls, "a resumed item must not be bought twice")
        # The point of carrying them forward: the paths survive the round trip.
        self.assertEqual(
            [i.companion_paths for i in first.items],
            [i.companion_paths for i in again.items],
        )


if __name__ == "__main__":
    unittest.main()
