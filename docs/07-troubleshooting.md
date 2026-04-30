# Troubleshooting Guide

Common issues and solutions for the FFT Channel Vocoder.

## Installation Issues

### "command not found: vocode"

**Problem**: The `vocode` command doesn't work

**Solutions**:
1. Make sure installation completed:
   ```bash
   pip3 install -e .
   ```

2. Use Python module syntax instead:
   ```bash
   python3 -m fft_channel_vocoder
   ```

3. On Windows, restart your terminal after installing

4. Check Python is in your PATH:
   ```bash
   which python3
   which pip3
   ```

5. Try reinstalling:
   ```bash
   pip3 uninstall fft_channel_vocoder
   pip3 install -e .
   ```

---

### "No module named 'numpy'"

**Problem**: Missing dependencies

**Solution**:
```bash
pip3 install numpy scipy mido
```

---

### "Permission denied" (macOS/Linux)

**Problem**: Can't install due to permissions

**Solutions**:
```bash
# Option 1: Use --user flag
pip3 install -e . --user

# Option 2: Use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
pip3 install -e .
```

---

## File Processing Issues

### "No input files found"

**Problem**: The vocoder can't find your audio files

**Checklist**:
1. ✓ Is the folder named exactly `input/`? (lowercase, not `Input/` or `INPUTS/`)
2. ✓ Does it exist in the same directory where you run `vocode`?
3. ✓ Are files in the `input/` folder directly, not in subfolders?
4. ✓ Are files named with correct extensions?
   - Voice files: `.wav` (lowercase)
   - MIDI files: `.mid` (lowercase)
   - Synth files: `.wav` (lowercase)

**Correct structure**:
```
your-project/
├── input/
│   ├── voice.wav
│   ├── melody.mid
│   └── synth.wav
└── (run vocode here)
```

**Try this**:
```bash
ls input/
# Should list your files
```

---

### "FileNotFoundError: input directory not found"

**Problem**: The `input/` folder doesn't exist

**Solution**:
```bash
mkdir input
# Copy your audio files to input/
cp ~/Music/voice.wav input/
cp ~/Music/melody.mid input/
vocode
```

---

### "Failed to load audio file: [filename]"

**Problem**: A file exists but can't be read

**Possible causes**:
- File is corrupted
- Wrong file format (e.g., MP3 instead of WAV)
- Unsupported MIDI format

**Solutions**:

1. **Check the file directly**:
   - Try opening in your DAW (Ableton, Logic, etc.)
   - Can you play it? If not, file is corrupted

2. **Convert audio to WAV**:
   ```bash
   # Using ffmpeg (install if needed)
   ffmpeg -i input_file.mp3 -acodec pcm_s24le -ar 96000 output.wav
   ```

3. **Verify MIDI file**:
   - Open in a DAW
   - Check for note events
   - Re-export if corrupted

4. **Check file size**:
   ```bash
   ls -lh input/
   ```
   - 0 bytes? File is empty, delete and re-get

---

## Audio Output Issues

### "Output files are silent (all zeros)"

**Problem**: Processing completes but output has no sound

**Common causes**:

1. **Input voice file is too quiet**
   - Voice signal too low → no spectral envelope extracted
   - Solution: Normalize before processing
   ```bash
   ffmpeg -i input.wav -af "loudnorm=I=-23:TP=-1.5" output.wav
   ```

2. **Carrier file is wrong**
   - Solution: Check carrier file plays in your DAW
   - Make sure file isn't silent

3. **Files have different sample rates causing mismatch**
   - Solution: Resample all files to same rate
   ```bash
   ffmpeg -i input.wav -ar 96000 output.wav
   ```

**Test this**:
```bash
# Play input files to verify they have sound
ffplay input/voice.wav
ffplay input/synth.wav
```

---

### "Output is just the carrier repeated"

**Problem**: Vocoding didn't work, output sounds like original carrier

**Causes**:
- Voice file is too quiet (spectral envelope too weak)
- Wrong file was used as voice

**Solution**:
1. Check input files:
   ```bash
   ffplay input/voice.wav
   # Should be speech or singing
   ffplay input/carrier.wav
   # Should be synth or noise
   ```

2. Ensure voice file is loud enough (-6 dB to -3 dB peak)

3. Check file naming — make sure you're using the right voice

---

### "Output sounds extremely distorted"

**Problem**: Output is clipping or full of artifacts

**Causes**:
- Input files are too loud (clipping)
- FFT size too small for the signal

**Solutions**:

1. **Normalize input files**:
   ```bash
   ffmpeg -i voice.wav -af "loudnorm" voice_norm.wav
   ffmpeg -i carrier.wav -af "loudnorm" carrier_norm.wav
   ```

2. **Increase FFT size** (see [Configuration Guide](05-configuration.md)):
   ```python
   fft_size_power = 13  # Instead of 12
   ```

3. **Reduce input amplitude** in your DAW
   - Aim for -6 dB peak level

---

### "Output sounds like robotic/metallic whisper"

**Problem**: Extreme robotic effect, even if that's not desired

**Causes**:
- Voice file is very noise or whisper (weak spectral envelope)
- FFT size too large (poor time resolution)

**Solutions**:

1. Use a clearer voice file (avoid whispers, heavy noise)

2. Try smaller FFT size:
   ```python
   fft_size_power = 11  # Instead of 12
   ```

3. Check voice file quality:
   ```bash
   ffplay input/voice.wav
   # Should be clear speech/singing, not whisper
   ```

---

### "Output sounds phasy or hollow"

**Problem**: Subtle phase artifacts or hollow quality

**This is usually normal** — slight phase artifacts are expected due to FFT nature.

**If problematic**:
1. Use larger FFT size:
   ```python
   fft_size_power = 13  # Better phase preservation
   ```

2. Blend with original carrier (see [Advanced Usage](06-advanced-usage.md)):
   ```python
   # 70% vocoded, 30% original
   output = 0.7 * vocoded + 0.3 * carrier
   ```

---

## Performance Issues

### "Processing is very slow"

**Typical times** (for reference):
- 30 seconds of audio: 5-10 seconds processing
- 5 minutes of audio: 1-2 minutes processing

**If slower than this**:

1. **Check system resources**:
   ```bash
   # macOS
   top -l 1 | grep -E "CPU|Mem"
   
   # Linux
   top -b -n 1 | head -20
   ```

2. **Reduce FFT size**:
   ```python
   fft_size_power = 11  # Faster, less accurate
   ```

3. **Lower sample rate**:
   ```python
   sample_rate = 44100  # Faster, lower quality
   ```

4. **Process shorter files** for testing

5. **Close other applications** to free RAM

---

### "Memory error / Out of memory"

**Problem**: System runs out of RAM during processing

**Causes**:
- File too large (>500 MB)
- FFT size too large
- Not enough free RAM

**Solutions**:

1. **Free up memory**:
   - Close unnecessary applications
   - Restart your computer

2. **Process smaller files**:
   - Split audio into 5-10 minute segments
   - Process separately

3. **Lower FFT size**:
   ```python
   fft_size_power = 10  # Uses less memory
   ```

4. **Lower sample rate**:
   ```python
   sample_rate = 44100  # Uses less memory
   ```

---

## MIDI Issues

### "MIDI file doesn't process"

**Problem**: MIDI file is ignored or causes errors

**Checks**:
1. Is the file extension `.mid` (not `.midi`)?
   ```bash
   # Rename if needed
   mv file.midi file.mid
   ```

2. Does the MIDI file have note events?
   - Open in DAW and check for notes

3. Is tempo reasonable (60-180 BPM)?

**Try this**:
```bash
# Re-export the MIDI from your DAW
# File → Export → MIDI
# Save as: melody.mid
```

---

### "MIDI synth sounds wrong"

**Problem**: Synthesized MIDI sounds metallic or odd

**This is normal** for simple sine wave synthesis. The vocoder applies spectral characteristics, creating the effect.

**To improve**:
- Use higher `sample_rate` (96000 or higher)
- Use larger `fft_size_power` (13 or 14)
- Or pre-synthesize the MIDI with your DAW and use WAV file instead

---

## File Format Issues

### "Unsupported file format"

**Problem**: File extension might be recognized but format isn't

**Solutions**:

1. **For WAV files**, ensure format is standard:
   ```bash
   # Check format details
   ffprobe -v error -select_streams a:0 \
     -show_entries stream=codec_name,sample_rate,bit_rate \
     -of default=noprint_wrappers=1 your_file.wav
   ```

2. **Convert to standard WAV**:
   ```bash
   ffmpeg -i input.wav -acodec pcm_s24le -ar 96000 output_standard.wav
   ```

3. **Supported formats**:
   - ✓ WAV (16-bit, 24-bit, 32-bit float)
   - ✓ MIDI (Type 0 and Type 1)
   - ✗ MP3 (convert to WAV first)
   - ✗ AAC/M4A (convert to WAV first)

---

## Configuration Issues

### "Changes to config.py don't take effect"

**Problem**: You edited `config.py` but settings don't change

**Solutions**:

1. **Reinstall to reload**:
   ```bash
   pip3 install -e . --force-reinstall --no-deps
   vocode
   ```

2. **Check you edited the right file**:
   ```bash
   cat fft_channel_vocoder/config.py
   # Should show your edits
   ```

3. **Make sure you saved**:
   - In your editor: Ctrl+S (or Cmd+S on Mac)

4. **Verify syntax is valid**:
   - Python is sensitive to spacing
   - Keep format like: `sample_rate = 96000`

---

## Platform-Specific Issues

### macOS Issues

**"zsh: command not found: vocode"**
- Make sure you use `python3` and `pip3` (not `python` or `pip`)

**"No such file or directory"**
- Use full paths: `/usr/local/bin/vocode` or `python3 -m fft_channel_vocoder`

---

### Windows Issues

**"The system cannot find the path specified"**
- Check that `input/` exists in current directory
- Use: `python -m fft_channel_vocoder` (might need python, not python3)

**"'vocode' is not recognized"**
- Restart Command Prompt or Powershell after installation
- Use: `python -m fft_channel_vocoder` as fallback

**Long file paths issue**
- Windows limits paths to 260 characters
- Keep your project folder name short

---

### Linux Issues

**"Permission denied" errors**
- Use `pip3 install --user` to install in home directory
- Or use a virtual environment

---

## Getting Help

If you can't find your issue:

1. **Gather information**:
   ```bash
   python3 --version
   pip3 --version
   ls -lh input/ output/
   ```

2. **Check related sections**:
   - [Installation Guide](01-installation.md)
   - [File Organization](04-file-organization.md)
   - [Configuration Guide](05-configuration.md)

3. **Try a minimal example**:
   - Use a short (5 second) voice file
   - Use a simple MIDI or synth
   - Run `vocode`
   - Check if issue still occurs

4. **Document the error**:
   - Exact error message
   - Your system (Windows/Mac/Linux)
   - Your Python version
   - Steps to reproduce

---

**Stuck on something specific?** Check [Understanding the Vocoder](03-understanding.md) for concepts or [Advanced Usage](06-advanced-usage.md) for complex workflows.
