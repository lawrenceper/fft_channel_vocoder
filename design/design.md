# Design Philosophy

## Overview

The FFT Channel Vocoder is designed with a clear mission: to create accessible, automated audio processing tools that empower creators of all abilities to participate in the indie artist scene.

## Design Principles

### 1. Accessibility by Design

This project exists because of frustration with inaccessible channel vocoder tools. Built by a blind tinkerer for blind tinkerers and everyone else who deserves equal access to audio tools.

> "I believe that every audio engineer and beginner should have equal access to technology, and this means audio and DSP tools. I want people with visual impairments to be able to participate in the Indie artist scene and this is one step to my goal. Accessibility is important to me, and so is empowering the world to create, to make, to build, without accessibility barriers."

**What this means in practice:**

- **CLI first, no GUI** — Screen readers work perfectly with command-line interfaces. No visual dependencies.
- **Semantic documentation** — All docs use proper heading hierarchy and semantic markup for screen readers
- **No visual-only features** — Every feature is accessible via text input and output
- **Cross-platform support** — Works on Mac, Windows, Linux, and even Raspberry Pi

### 2. Automation: Set It and Forget It

The vocoder is designed for hands-off batch processing. Point it at a folder of files, run the command, and let it work.

**Key automation features:**

- **Batch file discovery** — Automatically finds and processes files in standard patterns
- **Consistent naming** — Output files follow predictable conventions
- **Generator-based iteration** — Memory-efficient processing of large file sequences
- **No configuration required** — Sensible defaults work for most use cases

### 3. CLI First Architecture

The command-line interface is the primary interface, not an afterthought:

```bash
vocode              # Run with defaults
python -m fft_channel_vocoder  # Module syntax support
```

**Why CLI first?**

- Accessible to screen reader users
- Easy to script and automate
- Works in headless environments (servers, cloud, Raspberry Pi)
- Perfect for batch processing pipelines

### 4. Cross-Platform Compatibility

Runs on:

- **macOS** — Full support
- **Windows** — Full support  
- **Linux** — Full support
- **Raspberry Pi** — Full support (efficient audio processing)

No platform-specific code. Pure Python with standard libraries and well-maintained audio libraries.

### 5. Intelligent Algorithm Choice: Why FFT?

The vocoder uses Fast Fourier Transform (FFT) based spectral envelope transfer. This choice matters.

#### What is an FFT?

FFT (Fast Fourier Transform) converts audio from time-domain (samples over time) to frequency-domain (spectral content). This lets us analyze and modify what frequencies are present in audio.

#### Why FFT for Vocoding?

1. **Efficiency** — O(N log N) complexity. Can process long audio files quickly
2. **Spectral clarity** — Gives fine-grained control over frequency content
3. **Formant preservation** — Maintains the vocal character (what makes a voice sound like a voice)
4. **Carrier phase preservation** — Keeps the pitch and timing information from the carrier signal
5. **Simplicity** — Mathematically sound, well-understood algorithm

#### The Vocoding Problem

A vocoder needs to:

1. Extract the spectral envelope from a modulator (voice) — *what frequencies are emphasized*
2. Apply that envelope to a carrier (synth, MIDI, noise) — *impose voice character onto other sounds*
3. Preserve the carrier's pitch — *so output maintains the musical note*

FFT does all three naturally:

- **STFT Analysis** — Frame-based FFT captures time-varying spectral content
- **Envelope Extraction** — Gaussian blur isolates the smooth formant shape
- **Spectral Transfer** — Divide out carrier's envelope, multiply in voice envelope
- **Phase Preservation** — Keep carrier's phase (phase determines pitch)

#### Compared to Alternatives

| Approach | Pros | Cons | Use Case |
|---|---|---|---|
| **FFT (This vocoder)** | Fast, simple, good formant capture | Time-frequency tradeoff | General purpose, batch processing |
| **Phase Vocoder** | Excellent time-stretching | Complex phase reconstruction | Time-stretching, pitch-shifting |
| **Fixed-band** | Very fast, real-time capable | Artifacts at band boundaries | Low-latency, embedded systems |
| **Sinusoidal** | Highest quality | Computationally expensive | High-quality offline work |

We chose FFT because it's the sweet spot: efficient enough for batch processing, simple enough to understand, and powerful enough for professional results.

## Development Approach

### AI-Assisted Development

This project uses AI assistance throughout development:

- Architecture design with Claude
- Algorithm implementation with iterative refinement
- Testing and validation with AI support
- Documentation written collaboratively

**Why this matters:** The blind developer can describe what they want, work through problems with AI, and validate implementations through testing rather than visual inspection.

### Accessibility-First Development

Every feature is designed with accessibility as a requirement, not an afterthought:

1. Define what accessibility means for the feature
2. Implement with accessibility standards in mind
3. Test with accessibility tools (screen readers, keyboard navigation)
4. Document assuming the user cannot see the screen

## Design Decisions

### High Sample Rate (96 kHz)

Default to 96 kHz instead of 44.1 kHz:

- More headroom for processing without aliasing
- Better high-frequency representation
- Modern standard for professional audio
- Only slightly increased file sizes and processing time

### Gaussian Blur for Envelope Extraction

Using Gaussian blur (σ ≈ 10 FFT bins) to smooth the spectrum:

- Removes fine harmonic structure
- Preserves formant peaks (vocal character)
- Computationally efficient
- Perceptually aligned with how humans hear formants

### Carrier Phase Preservation

Output uses carrier's phase, not voice's phase:

- Maintains carrier pitch and timing (musically important)
- Avoids phase artifacts and "phasiness"
- Simpler algorithm than phase reconstruction
- Sounds more natural

## File Organization

The design favors **simplicity and predictability:**

```
input/
├── voice1.wav        # Modulator (voice)
├── voice2.wav        
├── melody1.mid        # Carrier (synthesized)
├── melody2.mid
├── synth1.wav         # Carrier (pre-generated)
└── synth2.wav

output/
├── voice1_melody1.wav   # Input: voice1 + melody1
├── voice1_melody2.wav   # Input: voice1 + melody2
├── voice1_synth1.wav    # Input: voice1 + synth1
├── voice1_synth2.wav    # Input: voice1 + synth2
└── voice1_whisper.wav   # Voice vocoded with noise
```

**Why this structure?**

- Predictable output naming enables further automation
- Generator-based file discovery is memory-efficient
- Supports large batch processing (100+ files)
- Easy to organize and find results

## Future Design Directions

Potential areas for expansion while maintaining core principles:

- **Real-time streaming** — Low-latency processing for live performance
- **Adaptive processing** — Adjust FFT size and smoothing based on signal content
- **Spectral morphing** — Blend between multiple voice envelopes
- **GPU acceleration** — Faster processing for very large batches
- **Plugin format** — DAW integration while preserving accessibility

All future work will maintain:

- CLI as primary interface
- Full screen reader accessibility
- Cross-platform compatibility
- Minimal external dependencies
