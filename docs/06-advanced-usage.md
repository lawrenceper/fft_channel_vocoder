# Advanced Usage Guide

Explore advanced workflows, batch processing, and custom Python usage.

## Table of Contents

1. [Batch Processing](#batch-processing)
2. [Python API](#python-api)
3. [Custom Workflows](#custom-workflows)
4. [Integration with DAWs](#integration-with-daws)
5. [Advanced Audio Techniques](#advanced-audio-techniques)

---

## Batch Processing

Process hundreds of files automatically without manual intervention.

### Large File Sets

The vocoder automatically processes all files in the `input/` folder:

```
input/
    voice_male_1.wav
    voice_male_2.wav
    voice_male_3.wav
    melody_1.mid
    melody_2.mid
    melody_3.mid
    synth_lead.wav
    synth_bass.wav
    synth_pad.wav
```

Running `vocode` processes:
- `voice_male_1` × all carriers (3 MIDI + 3 synth = 6 outputs)
- `voice_male_2` × all carriers (6 outputs)
- `voice_male_3` × all carriers (6 outputs)
- **Total**: 18 output files generated

**Processing order**: Deterministic (alphabetical by voice, then carrier)

### Organizing Batch Projects

For large batches, organize hierarchically:

```
batch-project/
    input/
        vocals/
            singer_1.wav
            singer_2.wav
        midi/
            melody.mid
            bass.mid
        synth/
            pad.wav
    output/
    log.txt (your notes)
```

**Note**: The vocoder expects files directly in `input/`, not subdirectories. For organizing batches:

**Option A: Symlink approach** (macOS/Linux)
```bash
cd input
ln -s ../vocals/*.wav .
ln -s ../midi/*.mid .
ln -s ../synth/*.wav .
vocode
```

**Option B: Copy files**
```bash
cp vocals/* input/
cp midi/* input/
cp synth/* input/
vocode
```

**Option C: Run multiple projects separately**
```bash
# Project 1: Singer A with all melodies
cd project-singer-a
vocode
cd ../project-singer-b
vocode
```

### Monitoring Large Batches

For multi-hour processing:

```bash
# Start in background, log output
vocode > batch_log.txt 2>&1 &

# Check progress periodically
tail -f batch_log.txt

# Check if finished
ls -lh output/ | wc -l
```

### Estimated Processing Times

| Input Size | Example | Processing Time |
|-----------|---------|-----------------|
| 3 voices × 5 carriers | 15 total | ~10 minutes |
| 10 voices × 10 carriers | 100 total | ~60 minutes |
| 20 voices × 20 carriers | 400 total | ~5 hours |

(On modern CPU, estimate: 1-2 minutes per output file at 96 kHz)

---

## Python API

Use the vocoder programmatically in Python code.

### Import and Basic Usage

```python
from fft_channel_vocoder.fft import vocode_signal
from fft_channel_vocoder.clean_io import load_audio, save_audio
import numpy as np

# Load voice and carrier
voice, sr_voice = load_audio("voice.wav")
carrier, sr_carrier = load_audio("synth.wav")

# Vocode
output = vocode_signal(voice, carrier)

# Save result
save_audio("output.wav", output, sr=96000)
```

### Core Functions

#### vocode_signal()

```python
from fft_channel_vocoder.fft import vocode_signal

output = vocode_signal(
    voice,        # numpy array, 1D or 2D
    carrier,      # numpy array, 1D or 2D
    sample_rate=96000  # Hz
)
# Returns: vocoded audio as numpy array
```

#### load_audio()

```python
from fft_channel_vocoder.clean_io import load_audio

audio, sample_rate = load_audio("file.wav")
# Returns: (audio_array, sample_rate_int)
```

#### save_audio()

```python
from fft_channel_vocoder.clean_io import save_audio

save_audio("output.wav", audio, sr=96000, bit_depth=24)
# Saves audio file with specified sample rate and bit depth
```

### Advanced: Custom Processing Loop

```python
from fft_channel_vocoder.fft import vocode_signal
from fft_channel_vocoder.clean_io import load_audio, save_audio

# Process multiple combinations
voices = ["voice1.wav", "voice2.wav"]
carriers = ["synth.wav", "melody.wav"]

for voice_file in voices:
    voice, sr = load_audio(f"input/{voice_file}")
    
    for carrier_file in carriers:
        carrier, sr = load_audio(f"input/{carrier_file}")
        
        # Vocode
        output = vocode_signal(voice, carrier)
        
        # Save
        output_name = f"{voice_file[:-4]}_{carrier_file[:-4]}.wav"
        save_audio(f"output/{output_name}", output, sr=96000)
        
        print(f"Saved: {output_name}")
```

### Advanced: Real-time Processing

For real-time or streaming use:

```python
from fft_channel_vocoder.fft import vocode_signal
import numpy as np

# Process in chunks
chunk_size = 4096  # samples
voice_chunk = np.random.randn(chunk_size)  # Your input
carrier_chunk = np.random.randn(chunk_size)

output_chunk = vocode_signal(voice_chunk, carrier_chunk)
# Process output_chunk immediately (send to speakers, etc.)
```

---

## Custom Workflows

### Workflow 1: AB Testing

Compare the vocoder with original signals:

```python
from fft_channel_vocoder.fft import vocode_signal
from fft_channel_vocoder.clean_io import load_audio, save_audio

voice, sr = load_audio("voice.wav")
carrier, sr = load_audio("carrier.wav")

# Original carrier
save_audio("output/original_carrier.wav", carrier, sr=sr)

# Vocoded
vocoded = vocode_signal(voice, carrier)
save_audio("output/vocoded.wav", vocoded, sr=sr)

# Voice alone (for reference)
save_audio("output/voice_alone.wav", voice, sr=sr)
```

Open all three in your DAW side-by-side for comparison.

### Workflow 2: Spectral Smoothing Variations

Test different formant extraction levels:

```python
from fft_channel_vocoder.fft import vocode_signal
from fft_channel_vocoder.clean_io import load_audio, save_audio
from scipy import ndimage

voice, sr = load_audio("voice.wav")
carrier, sr = load_audio("carrier.wav")

# Current: smooth with sigma=5
output_normal = vocode_signal(voice, carrier)
save_audio("output/vocoded_normal.wav", output_normal, sr=sr)

# Note: To test smoothing variations, you'd need to modify
# fft.py temporarily or create custom versions
```

### Workflow 3: Batch with Quality Levels

Process the same files at different quality settings using the configurator:

```bash
#!/bin/bash

# Function to update config using the configurator
update_config() {
    local sample_rate=$1
    local fft_size=$2
    python3 -c "
import json
from pathlib import Path

config_file = Path('fft_channel_vocoder/config.json')
config = json.loads(config_file.read_text())
config['sample_rate'] = $sample_rate
config['vocoder_fft_size'] = $fft_size
config_file.write_text(json.dumps(config, indent=2))
"
}

# Fast version
update_config 44100 10
vocode
mv output output_fast

# Standard version
update_config 96000 12
vocode
mv output output_standard

# High quality version
update_config 96000 13
vocode
mv output output_hq
```

**Or manually between runs**:
```bash
# Fast version
vocode --config
# Select 1, enter 44100, select 2, enter 10, select 6 to save
vocode
mv output output_fast

# Standard version
vocode --config
# Select 1, enter 96000, select 2, enter 12, select 6 to save
vocode
mv output output_standard

# High quality version
vocode --config
# Select 1, enter 96000, select 2, enter 13, select 6 to save
vocode
mv output output_hq
```

---

## Integration with DAWs

### Ableton Live Workflow

1. **Export stems** from your project
   - Export voice to `input/voice.wav`
   - Export synth/MIDI to `input/synth.wav` (synthesize MIDI first)

2. **Run vocoder**
   ```bash
   vocode
   ```

3. **Import output** back into your project
   - Drag `output/voice_synth.wav` into Ableton
   - Layer with original tracks

### Logic Pro Workflow

1. **Export audio files** from your arrangement:
   - Export voice to `input/voice.wav`
   - Export synth to `input/synth.wav`

2. **Run vocoder**
   ```bash
   vocode
   ```

3. **Import in Logic**:
   - Go to File, then Import, then Audio File
   - Select `output/voice_synth.wav`

### Reaper Workflow

Create a Reaper action to automate:

1. **Export stems to input/**
2. **Run vocoder** via action:
   ```
   Run shell command: vocode
   ```
3. **Watch output/** folder and import changes

---

## Advanced Audio Techniques

### Technique 1: Spectral Morphing

Create transitions between different vocal characters:

```python
from fft_channel_vocoder.fft import vocode_signal
from fft_channel_vocoder.clean_io import load_audio, save_audio
import numpy as np

voice1, sr = load_audio("voice_bright.wav")
voice2, sr = load_audio("voice_dark.wav")
carrier, sr = load_audio("synth.wav")

# Mix voices for "in-between" character
for alpha in [0.0, 0.25, 0.5, 0.75, 1.0]:
    mixed_voice = alpha * voice1 + (1 - alpha) * voice2
    vocoded = vocode_signal(mixed_voice, carrier)
    
    filename = f"output/morph_{int(alpha * 100):03d}.wav"
    save_audio(filename, vocoded, sr=sr)

# Sequence these files in your DAW for smooth morphing
```

### Technique 2: Parallel Vocoding

Blend vocoded and unvocoded signals:

```python
from fft_channel_vocoder.fft import vocode_signal
from fft_channel_vocoder.clean_io import load_audio, save_audio

voice, sr = load_audio("voice.wav")
carrier, sr = load_audio("carrier.wav")

# Vocoded version
vocoded = vocode_signal(voice, carrier)

# Mix: 70% vocoded, 30% original carrier
mix_ratio = 0.7
output = mix_ratio * vocoded + (1 - mix_ratio) * carrier

save_audio("output/parallel_vocoded.wav", output, sr=sr)
```

### Technique 3: Time-Varying Carrier

Use different carriers for different sections:

```python
from fft_channel_vocoder.fft import vocode_signal
from fft_channel_vocoder.clean_io import load_audio, save_audio
import numpy as np

voice, sr = load_audio("voice.wav")
synth1, sr = load_audio("synth1.wav")
synth2, sr = load_audio("synth2.wav")

# Vocode first half with synth1
voice_first = voice[:len(voice)//2]
voice_second = voice[len(voice)//2:]
synth1_first = synth1[:len(synth1)//2]
synth2_second = synth2[len(synth2)//2:]

output1 = vocode_signal(voice_first, synth1_first)
output2 = vocode_signal(voice_second, synth2_second)

output = np.concatenate([output1, output2])
save_audio("output/timevarying.wav", output, sr=sr)
```

### Technique 4: Spectral Layering

Vocode the same voice with multiple carriers and blend:

```python
from fft_channel_vocoder.fft import vocode_signal
from fft_channel_vocoder.clean_io import load_audio, save_audio

voice, sr = load_audio("voice.wav")
synth1, sr = load_audio("synth1.wav")
synth2, sr = load_audio("synth2.wav")

# Create three versions
output1 = vocode_signal(voice, synth1)
output2 = vocode_signal(voice, synth2)

# Equal blend
blended = (output1 + output2) / 2

save_audio("output/blended.wav", blended, sr=sr)
```

---

## Tips for Advanced Workflows

1. **Always backup originals** before processing
2. **Use version control** (git) for tracking audio experiments
3. **Document settings** used for each batch
4. **Monitor memory** for very large files (>100 MB)
5. **Use sample-accurate timing** when synchronizing with DAWs

---

**Need help with specific use cases?** Check [Troubleshooting](07-troubleshooting.md) or see [Understanding the Vocoder](03-understanding.md) for concepts.
