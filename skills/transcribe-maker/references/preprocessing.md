# Preprocessing for large files — transcribe-maker

Whisper API has a 25 MB upload limit. For larger files, preprocess with ffmpeg.

---

## Strategy 1: Re-encode audio to lower bitrate

For audio that's currently uncompressed or very high bitrate:

```bash
# WAV → MP3 64kbps (often 10× size reduction)
ffmpeg -i input.wav -b:a 64k input.mp3

# FLAC → MP3
ffmpeg -i input.flac -b:a 96k input.mp3
```

64-96 kbps mono is plenty for speech transcription (Whisper doesn't need high-fidelity audio).

---

## Strategy 2: Extract audio from video

If your input is a video, extract audio-only first:

```bash
# Extract audio (no re-encode if codec compatible)
ffmpeg -i video.mp4 -vn -acodec copy audio.aac

# OR re-encode to MP3 (more compatible)
ffmpeg -i video.mp4 -vn -b:a 64k audio.mp3
```

Then transcribe the audio file. Smaller than the original video.

---

## Strategy 3: Convert to mono

Stereo files are 2× larger than mono. Speech transcription doesn't need stereo:

```bash
ffmpeg -i input.mp3 -ac 1 -b:a 64k input-mono.mp3
```

---

## Strategy 4: Split into chunks

For long files (e.g., 2-hour podcasts), split into chunks <25 MB:

```bash
# Split into 15-minute chunks
ffmpeg -i input.mp3 -f segment -segment_time 900 -c copy chunk-%03d.mp3

# Then transcribe each chunk
for chunk in chunk-*.mp3; do
  transcribe-maker --input "$chunk" --format srt --output "${chunk%.mp3}.srt" --execute --yes
done

# Concatenate SRTs (will need timestamp adjustment — see below)
```

### Timestamp adjustment when concatenating chunks

Each chunk's SRT starts at 00:00. To merge into a single SRT with proper timestamps:

1. Compute the offset for each chunk: chunk N starts at `N * 900` seconds.
2. Shift each chunk's timestamps by that offset.
3. Merge.

Manual:
```bash
# (Pseudo — actual SRT timestamp manipulation needs a script)
# Tool: srt-tools / pysrt for programmatic shifts
pip install pysrt
```

Or skip concatenation and just keep per-chunk SRTs aligned with per-chunk videos.

---

## Strategy 5: Trim silence

If your file has long silences (e.g., poorly-edited recordings), trim them:

```bash
ffmpeg -i input.mp3 -af "silenceremove=stop_periods=-1:stop_duration=1:stop_threshold=-50dB" trimmed.mp3
```

This removes silences longer than 1 second below -50dB.

---

## Strategy 6: Increase compression aggressively

For absolute minimum file size (sacrificing audio quality but still transcribable):

```bash
ffmpeg -i input.mp3 -b:a 32k -ac 1 -ar 16000 ultra-small.mp3
```

- 32kbps mono at 16kHz sample rate
- Sounds awful, but Whisper still handles speech well

---

## Decision tree for file size

```
File >25 MB

  Is it video?
    Yes → extract audio (Strategy 2)
    No  → continue

  Is it >5 minutes?
    Yes → split into chunks (Strategy 4)
    No  → re-encode to lower bitrate (Strategy 1)

  Still >25 MB after that?
    → convert to mono (Strategy 3) + lower bitrate
    → trim silences (Strategy 5)
    → ultra-compress (Strategy 6, last resort)
```

---

## Pre-check command

Before calling transcribe-maker on a large file:

```bash
ls -lh input.mp3                  # check size
ffprobe input.mp3                 # check duration, codec, bitrate
```

If file >25 MB: preprocess first.

---

## File size estimation

Quick rules:
- MP3 64kbps mono: ~30 MB per hour of audio
- MP3 128kbps stereo: ~60 MB per hour
- WAV uncompressed: ~600 MB per hour
- M4A AAC 64kbps: ~30 MB per hour

For 1-hour content at typical podcast quality (64kbps mono MP3): fits in 25 MB limit if you trim it down.
