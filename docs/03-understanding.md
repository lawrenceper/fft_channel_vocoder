# Understanding the Vocoder

This guide explains what the vocoder does and the key concepts behind it.

## What is a Channel Vocoder?

A **channel vocoder** is an audio effect that combines the spectral characteristics of one signal (source) with the pitch and timing of another signal (carrier). The classic effect makes speech sound "robotic" when applied to a melody.

### Real-World Example

Imagine:
- **Source signal**: Your voice saying "hello"
- **Carrier signal**: A synthesized musical melody
- **Result**: The melody sounds like you're singing it, but with a robotic/synthetic quality

The vocoder extracts your voice's formants (characteristic frequencies) and applies them to the melody.

## Key Concepts for Audio Engineers

### Spectral Envelope

The **spectral envelope** is the overall frequency response curve of a sound — which frequencies are loud and which are quiet. Your voice has a unique spectral envelope:
- **Formants**: Peaks in the spectral envelope (around 1-4 kHz, 2-4 kHz, 3-5 kHz for vowels)
- **Resonances**: Natural peaks in your vocal tract

The vocoder extracts this envelope and transfers it to another signal.

### Modulator vs Carrier

- **Modulator** (source): Usually your voice — provides the spectral envelope
- **Carrier**: MIDI melody or synth wave — provides the pitch and timing

The output has:
- **Pitch** from the carrier
- **Spectral character** from the modulator

### Formants

**Formants** are resonant peaks in the vocal spectrum. For example:
- Vowel "A": Peaks around 700 Hz, 1200 Hz, 2600 Hz
- Vowel "E": Peaks around 550 Hz, 1700 Hz, 2600 Hz

These formants are what make vowels sound different. The vocoder preserves these to make processed speech intelligible.

## How This Vocoder Works (High Level)

### The 5-Step Process

1. **Analyze the voice** (STFT)
   - Convert voice to frequency domain using FFT
   - Captures formants and spectral characteristics

2. **Smooth the spectrum across frequency** (Gaussian blur)
   - Extracts the envelope (formant shape)
   - Removes fine pitch details so only the broad vocal shape remains
   - Low frequencies get stronger smoothing, high frequencies get lighter smoothing

3. **Smooth the envelope across time** (Temporal attack/release)
   - Allows energy to rise quickly (fast attack) to preserve sharp consonants like "t" and "k"
   - Allows energy to fall slowly (slow release) to sustain vowels naturally
   - This is what makes speech intelligible rather than washy or underwater-sounding

4. **Apply to carrier** (Spectral whitening + scaling)
   - Whiten the carrier spectrum (flatten frequency response)
   - Scale by the voice envelope

5. **Reconstruct audio** (Inverse STFT)
   - Convert back to time domain
   - Preserve the carrier's original phase (sounds natural)

For technical details, see [Algorithm Deep Dive](../design/algorithm.md).

## Why Use This Vocoder?

### Creative Applications

- **Vocal effects**: Create robotic or processed vocal sounds
- **Voice synth blending**: Blend vocals with instrumental melodies
- **Sound design**: Explore timbral transformations
- **Music production**: Add unique character to tracks

### Educational Value

- Learn FFT and spectral processing
- Understand formant extraction
- Study Python audio programming
- Implement classic DSP algorithms

## Audio Quality Considerations

### Sample Rate

This vocoder defaults to **96 kHz** for high-quality processing:
- Preserves up to 48 kHz frequencies
- Better formant accuracy than 44.1 kHz
- Larger file sizes and processing time

You can adjust in [Configuration Guide](05-configuration.md).

### FFT Size

The default FFT size is **4096 samples** (2^12):
- Good balance between frequency and time resolution
- Larger = more frequency precision, less time precision
- Smaller = less frequency precision, more time precision

For audio engineering, larger FFT sizes (8192 or 16384) give better formant resolution.

## Common Parameters to Understand

| Parameter | Purpose | Default |
|-----------|---------|---------|
| Sample rate | Audio resolution | 96 kHz |
| FFT size | Frequency resolution | 4096 |
| Hop size | Time between FFT frames | FFT size / 4 |
| Window function | Smoothing function | Hann window |

## What You'll Hear

### Ideal Results

- Voice characteristics clearly present in output
- Recognizable pitch/melody from carrier
- Natural-sounding formants
- Minimal artifacts

### Common Artifacts

- **Phasiness**: Slight phase distortion (normal)
- **Artifacts at edges**: Beginning/end of files (trim if needed)
- **Digital artifacts**: If input is very loud (normalize first)

See [Troubleshooting](07-troubleshooting.md) for solutions.

## Comparison to Other Vocoders

| Type | Vocoder | Bands | Use Case |
|------|---------|-------|----------|
| **Channel** | This one | ~20 fixed | Good quality, efficient |
| **Vocoder bank** | Signal Flow | 10-20 bands | Real-time, musical |
| **Phase vocoder** | Other tools | Continuous | Time-stretching, pitch-shifting |

This is a **spectral channel vocoder** — it analyzes the full spectrum smoothly, not with fixed bands.

## Next Steps

- Learn how to use it: [Quick Start](02-quick-start.md)
- Prepare your files: [File Organization](04-file-organization.md)
- Adjust settings: [Configuration Guide](05-configuration.md)
- Deep technical dive: [Algorithm Deep Dive](../design/algorithm.md)

---

**Questions about how it works?** Check the [Algorithm Deep Dive](../design/algorithm.md) for the math and signal processing details.
