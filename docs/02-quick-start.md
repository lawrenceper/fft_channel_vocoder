# Quick Start Guide

Get your first vocoded audio in 5 minutes!

## What You Need

1. **Audio files to work with**:
   - A voice file (WAV format) — your "modulator" signal
   - Either MIDI files or synth wave files (WAV) — your "carrier" signals

2. **The vocoder installed** — see [Installation Guide](01-installation.md)

## Step 1: Prepare Your Files (2 minutes)

Create a folder called `input` in your project directory:

```
input/
├── voice1.wav          # Your voice file
├── melody.mid          # A MIDI file (optional)
└── synth.wav           # A synth wave file (optional)
```

### Where to Get Sample Files

- **Voice files**: Record yourself speaking or singing, or download a vocal sample
- **MIDI files**: Create one in your DAW (like Ableton, Logic, or Reaper), or find free MIDI online
- **Synth waves**: Use the vocoder with pre-recorded synth waves

**Pro tip**: Start with short files (2-10 seconds) for faster processing while learning.

## Step 2: Run the Vocoder (1 minute)

Open a terminal in your project directory and run:

```bash
vocode
```

Or:
```bash
python3 -m fft_channel_vocoder
```

## Step 3: Check Your Output (30 seconds)

Your processed files appear in the `output/` folder:

```
output/
├── voice1_melody.wav       # Voice applied to melody
├── voice1_synth.wav        # Voice applied to synth
└── voice1_whisper.wav      # Voice applied to white noise
```

Open any file in your DAW or audio player to hear the results!

## What Just Happened?

The vocoder took your voice's spectral characteristics (formants) and applied them to your carrier signals. This creates the classic vocoder effect where your voice "shapes" the melody.

### Output Files Explained

| File | Input Used | Effect |
|------|-----------|--------|
| `voice1_melody.wav` | Voice + MIDI melody | Your voice applied to the synthesized melody |
| `voice1_synth.wav` | Voice + Pre-made synth | Your voice applied to the synth wave |
| `voice1_whisper.wav` | Voice + White noise | Robotic whisper effect |

## Next Steps

- **Customize settings**: See [Configuration Guide](05-configuration.md) to adjust sample rate or FFT size
- **Learn the concepts**: Read [Understanding the Vocoder](03-understanding.md)
- **Process more files**: Check [File Organization](04-file-organization.md) for organizing large batches
- **Troubleshoot issues**: Visit [Troubleshooting](07-troubleshooting.md) if something goes wrong

## Common Quick-Start Issues

**"No input files found"**
- Make sure you created the `input/` folder
- Check that your files are WAV (for voice/synth) or MID (for MIDI)

**"FileNotFoundError"**
- Make sure `input/` is in the same directory where you run `vocode`

**"Output files are silent"**
- Check that your input files aren't too quiet (amplify them if needed)
- See [Troubleshooting](07-troubleshooting.md)

---

**Ready to learn more?** Jump to [Understanding the Vocoder](03-understanding.md) or [File Organization](04-file-organization.md).
