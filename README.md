# FFT Channel Vocoder

A Python package that applies spectral envelope transfer using FFT-based processing. The vocoder takes a modulator (voice) signal and imposes its spectral envelope onto a carrier signal.

Designed with accessibility as a core principle: CLI first, no GUI, cross-platform, automated batch processing—built by a blind developer for everyone who deserves equal access to audio tools.

## Documentation

- 📚 **[Documentation](docs/index.md)** — Installation, tutorials, configuration, and troubleshooting
- 🎨 **[Design Philosophy](design/index.md)** — Why we built it this way, design decisions, and algorithm choices
- ⚙️ **[Algorithm Deep Dive](design/algorithm.md)** — Technical details for audio engineers and researchers

## Features

- **Spectral Envelope Transfer**: Extracts formant information from voice and applies it to carrier signals
- **Multiple Input Formats**: Supports voice files, MIDI files (synthesized to carrier waves), and pre-generated synth wave files
- **Batch Processing**: Automatically processes multiple input files with consistent naming patterns
- **Generator-based Design**: Uses Python generators for efficient iteration through numbered file sequences
- **Accessibility First**: CLI interface, fully accessible to screen readers, works across platforms

## Installation

### From source
```bash
cd fft_channel_vocoder
pip install -e .
```

## Usage

### Command Line

Run the vocoder via the `vocode` command:
```bash
vocode
```

Or using Python module syntax:
```bash
python3 -m fft_channel_vocoder
```

### Input Structure

The vocoder expects files organized in an `input/` directory:

```
input/
├── voice1.wav          # Modulator signals
├── voice2.wav
├── melody1.mid         # MIDI files to synthesize as carrier
├── melody2.mid
├── synth1.wav          # Pre-generated synth wave files as carrier
├── synth2.wav
└── synth3.wav
```

### Processing Flow

For each voice file, the vocoder:

1. **MIDI Processing**: Synthesizes each MIDI file into a carrier wave and vocodes with the voice
2. **Synth Wave Processing**: Loads each pre-generated synth wave file and vocodes with the voice
3. **Whisper Generation**: Creates a stereo whisper track by vocoding the voice with white noise

### Output Structure

Processed files are saved to `output/`:

```
output/
├── voice1_melody1.wav       # Voice + MIDI synthesis
├── voice1_melody2.wav
├── voice1_synth1.wav        # Voice + Synth wave 1
├── voice1_synth2.wav
├── voice1_synth3.wav
└── voice1_whisper.wav       # Stereo whisper track
```

## Configuration

Edit `fft_channel_vocoder/config.py` to adjust:

- `sample_rate`: Default 96,000 Hz
- `fft_size`: FFT window power (2^12 = 4096 samples)

## Algorithm

The vocoder works in 4 steps:

1. **STFT Analysis**: Compute Short-Time Fourier Transform for both voice and carrier
2. **Spectral Smoothing**: Apply Gaussian blur to extract formant envelopes
3. **Envelope Transfer**: Apply spectral whitening to the carrier, then scale by voice envelope
4. **Reconstruction**: Inverse STFT with original carrier phase to recover time-domain signal

## Module Reference

- `main.py`: Core pipeline and file iteration
- `fft.py`: FFT vocoding algorithm
- `clean_io.py`: Audio file I/O with resampling
- `clean_audio.py`: Audio preprocessing and validation
- `config.py`: Global configuration parameters
- `midi_synth.py`: MIDI to audio synthesis
- `noise_generators.py`: Noise generation utilities
- `buffers.py`: Buffer management utilities
