# File Organization Guide

Proper file organization ensures smooth processing and easy management of your audio projects.

## Input Folder Structure

The vocoder requires an `input/` folder in your working directory:

```
your-project/
    input/
        voice1.wav
        voice2.wav
        melody1.mid
        melody2.mid
        synth1.wav
        synth2.wav
    output/
        (automatically created)
```

## File Types Supported

### Voice Files (Modulators)

**Format**: WAV files  
**Purpose**: Provides the spectral envelope (formants)

Requirements:
- **Mono or stereo** — both work (stereo averaged to mono internally)
- **Mono recommended** — clearer spectral characteristics
- **Sample rate**: Any rate — will be resampled to your configured rate
- **Bit depth**: 16-bit or 24-bit recommended
- **Duration**: 2 seconds to 10 minutes

**Tips for good voice files**:
- Clear, dry vocals work best
- Minimize background noise
- Normalize to around -3dB peak level
- Avoid very quiet or very loud files

Example:
```
input/
    vocal_female.wav
    vocal_male.wav
    speech_english.wav
    laughter.wav
```

### MIDI Files (Carriers)

**Format**: .mid files  
**Purpose**: Provides pitch and timing

The vocoder synthesizes MIDI to audio automatically.

Requirements:
- **Note events**: MIDI notes with velocity
- **Tempo**: Any tempo (detected from MIDI)
- **Format**: Standard MIDI files (Type 0 or Type 1)
- **Duration**: Up to 10 minutes

**Tips for good MIDI**:
- Use reasonable tempos (60-180 BPM for clarity)
- Include note velocity variation for realism
- Short notes (0.5-1 sec) for articulate effects
- Long notes (1-5 sec) for legato effects

Example:
```
input/
    melody1.mid
    arpeggio1.mid
    bass_line.mid
    chord_progression.mid
```

### Synth Wave Files (Carriers)

**Format**: WAV files (pre-generated synth waveforms)  
**Purpose**: Provides pre-made carrier signals

Requirements:
- **Mono or stereo** — both work
- **Mono recommended** — clearer vocoder effect
- **Sample rate**: Any rate — resampled automatically
- **Waveform**: Any synth sound (saw, sine, square, noise, etc.)

**Tips for good synth files**:
- Consistent tone throughout
- Moderate loudness (-12dB to -6dB peak)
- Simple waveforms (saw, sine) work better than complex
- Can be any duration

Example:
```
input/
    saw_wave.wav
    sine_wave.wav
    square_wave.wav
    noise_pink.wav
    pad_synth.wav
```

## Naming Conventions

The vocoder automatically processes all files and creates outputs with predictable names.

### Naming Rule

Output files follow the pattern: `{voice_name}_{carrier_name}.wav`

### Example Naming

**Input files**:
```
input/
    voice1.wav          # Voice
    melody1.mid         # MIDI
    synth1.wav          # Synth wave
```

**Output files**:
```
output/
    voice1_melody1.wav     # voice1 + melody1
    voice1_synth1.wav      # voice1 + synth1
    voice1_whisper.wav     # voice1 + white noise (automatic)
```

### Best Practices

- **Use descriptive names**: `vocal_female.wav` instead of `v1.wav`
- **Avoid special characters**: Use hyphens and underscores only
- **Include artist/instrument**: `voice_amy_singing.wav`
- **Version numbers**: `melody_demo_v2.mid`

Good naming:
```
vocal_female_bright.wav
melody_pop_32bars.mid
synth_lead_aggressive.wav
```

Avoid:
```
voice (1).wav
melodyyy!!!.mid
audio-file-with-non-ASCII-characters.wav
```

## Organizing Multiple Projects

### Project Structure

```
vocoder-projects/
    project-1-pop-song/
        input/
            vocal.wav
            melody.mid
            bass.mid
        output/
    project-2-experimental/
        input/
            speech.wav
            synth1.wav
            synth2.wav
        output/
    project-3-batch-test/
        input/
        output/
```

### Running Multiple Projects

Navigate to each project and run:
```bash
cd project-1-pop-song
vocode
```

Each project maintains its own `input/` and `output/` folders.

## File Size and Performance

### Typical File Sizes

| Content | Duration | File Size |
|---------|----------|-----------|
| Voice (96 kHz, 24-bit) | 1 min | ~25 MB |
| Voice (96 kHz, 24-bit) | 5 min | ~130 MB |
| MIDI melody | Any | ~10-50 KB |
| Synth wave (96 kHz, 24-bit) | 1 min | ~25 MB |

### Processing Time (Approximate)

On modern hardware:
- 30 seconds of audio: 5-10 seconds processing
- 5 minutes of audio: 1-2 minutes processing
- 10 minutes of audio: 3-5 minutes processing

**Tip**: Start with short files (10-30 seconds) while experimenting.

## Handling Special Cases

### Multiple Voice Files

The vocoder processes each voice with all carriers:

```
input/
    voice1.wav      produces  voice1_melody1.wav
    voice2.wav      produces  voice2_melody1.wav
    melody1.mid
```

### Stereo Voice Files

**Best approach**: Convert to mono first using your DAW or:
```bash
ffmpeg -i voice_stereo.wav -ac 1 voice_mono.wav
```

The vocoder handles stereo but averages to mono internally.

### Very Long Files

For audio longer than 10 minutes:
- Split into segments in your DAW
- Process segments separately
- Concatenate outputs

## Pre-Processing Tips

### Normalize Audio

Audio should peak around -3dB:
- Use your DAW's normalize function
- Or use command line: `ffmpeg -i input.wav -af "loudnorm" output.wav`

### Remove Silence

For faster processing, trim silence:
- Use your DAW's silence removal
- Or: `ffmpeg -i input.wav -af "silenceremove=1:0:-50dB" output.wav`

### Resample to Processing Rate

Pre-resample to 96 kHz if your files are at different rates:
```bash
ffmpeg -i input.wav -ar 96000 output.wav
```

## Troubleshooting File Issues

**"No input files found"**
- Ensure `input/` folder exists
- Check file extensions (.wav, .mid are lowercase)

**"Failed to load audio file"**
- File might be corrupted
- Try opening in your DAW first
- Check file format is actually WAV or MIDI

**"Output files are silent"**
- Input voice file might be too quiet
- Try normalizing input files (see above)

---

**Ready to process files?** See [Quick Start](02-quick-start.md) or [Configuration Guide](05-configuration.md).
