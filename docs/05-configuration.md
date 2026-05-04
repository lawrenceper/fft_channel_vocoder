# Configuration Guide

Settings are stored in `fft_channel_vocoder/config.json`. This file is created automatically on first run with sensible defaults.

## Settings

### sample_rate

The number of audio samples per second. Higher values capture more detail but take longer to process and produce larger files.

- 44100 — Standard CD quality, fastest processing
- 48000 — Standard for video and film
- 96000 — High resolution, good for music production
- 192000 — Mastering quality, slowest processing

Default is 44100.

### vocoder_fft_size

The window size used for frequency analysis, entered as a power of 2. The actual window size is 2 raised to this number. For example, a value of 12 means a window of 4096 samples.

A larger value gives more precise frequency detail but reacts more slowly to changes in the voice. A smaller value reacts faster but captures less frequency detail.

- 10 — 1024 samples, fast testing
- 11 — 2048 samples
- 12 — 4096 samples, default, good balance
- 13 — 8192 samples, better formant capture
- 14 — 16384 samples, detailed analysis, slowest

### vocoder_hop

Controls how much the analysis window advances between each step, as a divisor of the FFT size. A value of 4 means the window moves forward by one quarter of the FFT size each step.

Higher values mean more overlap between windows, which produces smoother output but takes longer. Lower values are faster but less smooth.

- 1 — Largest steps, fastest, least smooth
- 4 — Default, recommended for most uses
- 8 — Smallest steps, smoothest, slowest

### pitch_correct_fft_size

Same as `vocoder_fft_size` but for the pitch correction step. You can adjust this independently from the vocoder. Uses the same power-of-2 values.

### pitch_correcter_hop

Same as `vocoder_hop` but for the pitch correction step.

## Opening the Configurator

The easiest way to change settings is the built-in interactive configurator. Run:

```bash
vocode --config
```

Or use the short form:

```bash
vocode -c
```

The menu lists all current settings and lets you pick one to change by number. After making changes, select the exit option to save. Settings take effect on the next run of `vocode`.

## Editing config.json Directly

Advanced users can open `fft_channel_vocoder/config.json` in any text editor. The file looks like this:

```json
{
  "sample_rate": 44100,
  "vocoder_fft_size": 12,
  "vocoder_hop": 4,
  "pitch_correct_fft_size": 12,
  "pitch_correcter_hop": 4
}
```

Change any value and save the file. The next run of `vocode` will use the new settings.

## Scale File Format

Scale files live in the `input/` folder as `scale1.txt`, `scale2.txt`, and so on. Each line is a note name. Lines starting with `#` are comments.

```
# C major pentatonic
c
d
e
g
a
```

You can add optional frequency range limits to reduce false pitch detections from sibilant sounds like S and T:

```
min_freq=80
max_freq=400
```

If high notes or sibilants are being incorrectly detected as pitch, lower `max_freq`. If low-pitched sections are being missed, lower `min_freq`.

---

For help with file organization, see [File Organization](04-file-organization.md).

For algorithm details, see [Algorithm Deep Dive](../design/algorithm.md).
