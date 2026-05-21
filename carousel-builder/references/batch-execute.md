# Batch execute — how the carousel runner works

The `--execute` flag invokes `common.runners.batch.run_batch()` under the hood. This file documents how it works, manifest format, retry semantics, failure handling.

---

## Manifest format

`./generated/carousel/<slug>/manifest.json`:

```json
{
  "schema": "skills.batch.v1",
  "updated_at": "2026-05-21T14:23:01Z",
  "meta": {
    "skill": "carousel-builder",
    "topic": "AI productivity tools for solo founders",
    "platform": "instagram",
    "aspect": "portrait",
    "style_id": "kinfolk-minimal",
    "model": "flux-2-pro",
    "text_mode": "embedded",
    "research_brief": "./generated/research/ai-productivity-tools-...md",
    "estimated_total_cost_usd": "0.48"
  },
  "items": [
    {
      "index": 1,
      "label": "slide-01-hook",
      "prompt": "<full per-slide prompt incl. style anchor>",
      "kwargs": {"size": "1080x1350"},
      "status": "succeeded",
      "output_path": "./generated/carousel/.../slide-1.png",
      "s3_url": "https://...",
      "error": null,
      "started_at": 1716297781.21,
      "finished_at": 1716297787.49
    },
    {
      "index": 2,
      "label": "slide-02-point",
      "prompt": "...",
      "kwargs": {"size": "1080x1350"},
      "status": "failed",
      "output_path": null,
      "s3_url": null,
      "error": "[flux-2-pro 429] rate limit exceeded",
      "started_at": 1716297787.50,
      "finished_at": 1716297788.10
    }
  ]
}
```

---

## Lifecycle

1. **Plan**: skill builds N `BatchItem` objects (one per slide).
2. **Estimate**: `estimate_batch_cost(provider, items)` → sum across all items.
3. **Confirm**: `confirm_batch(total, n_items=N, modality="carousel", yes=args.yes)` — asks once.
4. **Manifest init**: write items list with all `status: "pending"`.
5. **Parallel execute**: ThreadPoolExecutor with `parallelism` workers. Each worker:
   - Calls `provider.generate(prompt, **kwargs)`.
   - If JobHandle returned: `provider.poll(handle, timeout=poll_timeout)`.
   - On GenerationResult: `output.save()` to local + optional S3.
   - On exception: capture error, mark failed.
   - Write manifest after each item (state change).
6. **Final**: return BatchResult with items list partitioned succeeded / failed.

---

## Retry semantics

- **No automatic retries** within a single run. If a slide fails, it stays failed.
- **`--resume`**: load manifest, skip items with `status: "succeeded"`, re-attempt items with `status: "failed"` or `status: "pending"`.
- For transient failures (429, 502, 503): `--resume` is the recovery path. Just re-run with `--resume` and the failed items pick up.

---

## Parallelism caveats

- Default 3. Safe for OpenAI / Google / BFL native APIs.
- Some providers throttle at lower parallelism: Suno is 1-2, Lyria is 1, Eleven Music is 2. These apply to MUSIC, not images, but worth noting if carousel-builder is ever extended.
- For Flux router providers (fal.ai, Replicate): can usually push to 5-6 concurrent.
- Max enforced: 6. Beyond that, vendor APIs tend to 429.

Override: `--parallelism N`.

---

## Failure modes + recovery

### Single slide fails mid-batch

- Manifest captures the error string and the prompt.
- Other slides continue.
- Exit code: 1 (non-fatal — some slides succeeded).
- Recovery: `carousel-builder --resume <slug-or-output-dir>` — retries only failed.

### All slides fail (auth, bad model, etc)

- All marked failed.
- Skill prints aggregate error reason.
- Exit code: 1.
- Recovery: fix env vars / model selection, then `--resume`.

### Generation succeeds but file write fails (disk full, permissions)

- `save()` raises OSError.
- Worker catches, marks failed with the OSError message.
- Recovery: fix disk, `--resume`.

### Cost-confirmation declined

- `CostConfirmationDeclined` raised.
- NO generations triggered.
- Prompts.md is still written (since prompts were assembled before the confirmation).
- Exit code: 3.
- Recovery: re-run with `--yes` if you've reviewed prompts.

### API key missing for chosen model

- `KeyMissingError` raised at first item.
- Manifest marks ALL items failed with "missing env: $X".
- Prompts saved to `prompts.md`.
- Exit code: 2.
- Recovery: set env var, then `--resume` (which will re-run everything since all marked failed) or just re-run from scratch.

---

## Prompt fallback (always written)

`./generated/carousel/<slug>/prompts.md` is written BEFORE any generation starts. Contains:

```markdown
# Per-slide prompts — <topic> · <model> · <style-id>

## Common anchor (applied to every slide)

> <style anchor text>

---

## Slide 1 — hook · slide-01-hook

```
<full prompt text including anchor + slide content + composition + aspect>
```

(*if embedded text*) Headline embedded: "<exact text>"

---

## Slide 2 — point · slide-02-point

```
<full prompt text>
```

...
```

The user can copy any of these prompts and paste manually into Midjourney / a provider's UI if the API generation fails.

---

## --resume behaviour

`carousel-builder --resume <output-dir>` OR `--resume` alone (uses current dir convention):

1. Read manifest.json from output dir.
2. For each item:
   - `succeeded` → skip (already saved at output_path).
   - `failed` or `pending` → re-execute with the SAME prompt as last time.
3. Re-confirm cost ONLY if there are pending/failed items totaling >$0.10.
4. Run batch on the pending subset.
5. Write final stats: "X already succeeded, Y newly succeeded, Z still failed".

Resume does NOT re-assemble prompts. The prompts in the manifest are the source of truth. To FORCE prompt regeneration, delete manifest.json and re-run from scratch.

---

## Output paths convention

- `slide-N.<ext>` where N is the index (1-based, 2-digit unnecessary for ≤12 slides but optional)
- Slug suffix omitted from filenames (the directory has it)
- Extension comes from the provider's GenerationResult.extension (typically `png` for images)

S3 uploads (if `S3_*` env vars set): mirror to `<bucket>/<S3_PATH_PREFIX>/carousel/<slug>/slide-N.png`. URL appended to manifest's `s3_url` field per item.
