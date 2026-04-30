# Configuration Guide

Learn how to customize the vocoder's settings for your specific needs.

## Overview

Configuration is stored in `fft_channel_vocoder/config.py`. This guide explains each setting and how to adjust them.

## Accessing Configuration

### Current Configuration File

Located at: `fft_channel_vocoder/config.py`

Example:
```python
sample_rate = 96000  # Hz
fft_size_power = 12  # 2^12 = 4096
```

## Main Settings

### Sample Rate

**What it is**: Audio resolution (samples per second)

**Current setting**:
```python
sample_rate = 96000  # Hz (96 kHz)
```

**Available options**:
- `44100` — Standard CD quality (smaller files, faster)
- `48000` — Standard for video/film
- `96000` — High resolution (default, better quality)
- `192000` — Mastering quality (largest files, slowest)

**How it affects your audio**:
- Higher = Better high-frequency capture, clearer formants, larger files
- Lower = Faster processing, smaller files, less detail

**For different use cases**:
```python
# Streaming / Fast testing
sample_rate = 44100

# Professional mixing
sample_rate = 96000

# Mastering / Research
sample_rate = 192000
```

**Memory usage**:
- 1 minute at 44.1 kHz: ~5 MB
- 1 minute at 96 kHz: ~11 MB
- 1 minute at 192 kHz: ~23 MB

### FFT Size

**What it is**: Window size for frequency analysis (power of 2)

**Current setting**:
```python
fft_size_power = 12  # 2^12 = 4096 samples
```

**Understanding the power**:
- `2^10` = 1024 samples
- `2^11` = 2048 samples
- `2^12` = 4096 samples (default)
- `2^13` = 8192 samples
- `2^14` = 16384 samples

**Frequency resolution** (how precise formant detection is):

At 96 kHz sample rate:
- `fft_size_power = 10` (1024): ~94 Hz per bin (poor)
- `fft_size_power = 11` (2048): ~47 Hz per bin (okay)
- `fft_size_power = 12` (4096): ~23 Hz per bin (good) ← default
- `fft_size_power = 13` (8192): ~12 Hz per bin (excellent)
- `fft_size_power = 14` (16384): ~6 Hz per bin (very fine)

**Time resolution** (how quickly changes are detected):

At 96 kHz sample rate:
- `fft_size_power = 12` (4096): ~43 ms (good for speech)
- `fft_size_power = 13` (8192): ~85 ms (slower)
- `fft_size_power = 14` (16384): ~170 ms (very slow)

**Trade-off**:
- **Larger FFT** → Better frequency precision, worse time resolution
- **Smaller FFT** → Worse frequency precision, better time resolution

**Recommendations by use case**:

```python
# Fast testing / Real-time requirements
fft_size_power = 10  # 1024 samples

# General music production (default)
fft_size_power = 12  # 4096 samples

# High-quality formant preservation
fft_size_power = 13  # 8192 samples

# Research / Detailed analysis
fft_size_power = 14  # 16384 samples
```

**Performance impact**:
- Doubling FFT size roughly doubles processing time
- Doubling FFT size roughly halves files sizes (with same sample rate)

## How to Change Settings

### Method 1: Edit config.py Directly

1. Open `fft_channel_vocoder/config.py` in a text editor
2. Modify the values:
   ```python
   sample_rate = 96000
   fft_size_power = 12
   ```
3. Save the file
4. Run the vocoder: `vocode`

**Example: High-quality settings**
```python
# For best formant capture (slower processing)
sample_rate = 96000
fft_size_power = 13
```

**Example: Fast testing**
```python
# For quick experiments (less quality)
sample_rate = 44100
fft_size_power = 10
```

### Method 2: Environment Variables (Future)

For future versions, you may be able to set:
```bash
export VOCODER_SAMPLE_RATE=48000
export VOCODER_FFT_SIZE=11
vocode
```

(Check if supported in your version)

## Configuration Profiles

Create different configuration files for different workflows:

### Setup

Create a copy of config.py for each use case:

```bash
cp fft_channel_vocoder/config.py fft_channel_vocoder/config_fast.py
cp fft_channel_vocoder/config.py fft_channel_vocoder/config_hq.py
```

### Fast Profile (testing)

`config_fast.py`:
```python
sample_rate = 44100      # Quick processing
fft_size_power = 10      # Small FFT
```

### High-Quality Profile (production)

`config_hq.py`:
```python
sample_rate = 96000      # High resolution
fft_size_power = 13      # Large FFT for detail
```

Then in your code (advanced):
```python
# Load custom config
import importlib.util
spec = importlib.util.spec_from_file_location("config", "config_hq.py")
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
```

## Recommended Settings by Use Case

### Music Production

```python
sample_rate = 96000       # Professional quality
fft_size_power = 12       # Good frequency resolution
```

**Processing**: 1-2 minutes per audio minute

### Real-Time / Live Performance

```python
sample_rate = 48000       # Fast processing
fft_size_power = 10       # Smaller window
```

**Processing**: Near real-time (depends on audio length)

### Research / Analysis

```python
sample_rate = 192000      # Maximum detail
fft_size_power = 14       # Fine frequency analysis
```

**Processing**: 3-5x slower, best results

### Streaming / Previews

```python
sample_rate = 44100       # Compact files
fft_size_power = 10       # Fast processing
```

**Processing**: Very fast, adequate quality

## Advanced Settings (Technical)

These are derived from the two main settings — usually don't change:

### Hop Size

Calculated automatically as: `fft_size / 4`

- At fft_size_power = 12: hop_size = 1024
- At fft_size_power = 13: hop_size = 2048

Larger = fewer overlaps = faster but less smooth
Smaller = more overlaps = slower but smoother

### Window Function

Currently uses **Hann window** for smooth analysis. This is optimal for most cases.

## Performance Tuning

### For Faster Processing

1. Lower `sample_rate` to 44100
2. Lower `fft_size_power` to 10 or 11
3. Trim long silences from input files

**Example fast config**:
```python
sample_rate = 44100
fft_size_power = 10
```

### For Better Quality

1. Raise `sample_rate` to 96000 or 192000
2. Raise `fft_size_power` to 13 or 14
3. Use longer input files (more context for formant extraction)

**Example quality config**:
```python
sample_rate = 96000
fft_size_power = 13
```

## Testing Your Configuration

### Quick Test

1. Set new configuration
2. Run on a short (5-10 second) audio file
3. Check the output
4. Adjust and repeat

**Sample test command**:
```bash
# Change config.py
vocode

# Listen to output/
# Not happy? Edit config.py again and vocode
```

### Before/After Comparison

Process the same input with different configurations:

```bash
# Fast version
# Edit config.py to fast settings
vocode
mv output output_fast

# Reinstall to reload config
pip install -e .

# HQ version
# Edit config.py to HQ settings
vocode
mv output output_hq

# Compare output_fast and output_hq
```

## Troubleshooting Configuration

**"Settings don't seem to change"**
- Make sure you saved `config.py`
- If you installed with `pip install -e .`, the changes should be immediate
- Try: `pip install -e . --force-reinstall` to reload

**"Processing is too slow"**
- Lower `sample_rate` to 44100
- Lower `fft_size_power` to 11
- Process shorter audio files for testing

**"Quality is too low"**
- Raise `sample_rate` to 96000 or higher
- Raise `fft_size_power` to 13
- Ensure input voice files are high quality

**"Audio sounds robotic/artifacts"**
- Try larger `fft_size_power` (13 or 14) for better formant capture
- Ensure input voice files aren't clipped
- See [Troubleshooting](07-troubleshooting.md)

---

**Want to understand the algorithm?** See [Algorithm Deep Dive](../design/algorithm.md).

**Need help with files?** Check [File Organization](04-file-organization.md).
