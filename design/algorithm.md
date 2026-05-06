# Algorithm Deep Dive

Technical details of the FFT vocoding algorithm for audio engineers and researchers.

## Overview

The FFT Channel Vocoder implements spectral envelope transfer using five main steps:

1. **STFT Analysis** — Compute frequency domain representation
2. **Envelope Extraction** — Smooth spectrum across frequency to isolate formants
3. **Temporal Envelope** — Apply asymmetric attack/release smoothing across time
4. **Spectral Transfer** — Apply voice envelope to carrier
5. **STFT Synthesis** — Reconstruct time-domain audio

## 1. STFT Analysis

### Short-Time Fourier Transform (STFT)

The STFT divides audio into overlapping frames and applies FFT to each:

```
Voice signal:    ✂️ ✂️ ✂️ ✂️    (framing)
                  ↓  ↓  ↓  ↓
Frames:          [-----] (with overlap)
                  [  -----]
                    [  -----]
                      [  -----]
                         ↓
FFT on each frame     X[k,t] (complex spectrum)
```

### Parameters

- **Sample rate**: 96,000 Hz (default, configurable)
- **FFT size**: 2^12 = 4,096 samples (default, configurable)
- **Hop size**: FFT_size / 4 = 1,024 samples (75% overlap)
- **Window**: Hann window (smooth edges to avoid artifacts)

### Time-Frequency Resolution

At 96 kHz with FFT size 4096:

```
Frequency resolution: 96000 / 4096 ≈ 23.4 Hz per bin
Time resolution: 4096 / 96000 ≈ 42.7 ms per frame
```

This balance:
- ✓ Fine enough to capture formants (~100-300 Hz spacing)
- ✓ Fast enough to track formant motion over time

### Output

For each frame `t` and frequency bin `k`:
```
Voice[k,t] = |Voice[k,t]| * e^(i*phase_voice[k,t])
Carrier[k,t] = |Carrier[k,t]| * e^(i*phase_carrier[k,t])
```

Where:
- `|·|` = magnitude spectrum
- `e^(i*φ)` = phase spectrum

## 2. Envelope Extraction (Spectral Smoothing)

### Gaussian Blur

The vocoder applies Gaussian blur to the magnitude spectrum to extract the **envelope** (smooth formant shape):

```
Original spectrum:    ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁  (detailed)
                              ↓
Gaussian blur         ▁▂▃▅▆█▆▅▃▂▁      (smooth envelope)
(σ ≈ 8-16 bins)       
```

### Why Gaussian Blur?

- Removes fine-structure (spectral peaks from individual harmonics)
- Preserves formant shape (important for vocal character)
- Computationally efficient

### Mathematical Details

```
Envelope[k] = Σ(Weight(k-k') × Magnitude[k']) for all k'
            = Gaussian convolution of magnitude spectrum
```

Where `Weight` is a Gaussian function:
```
Weight(δk) = exp(-(δk)² / (2σ²))
σ ≈ 10 bins (standard deviation)
```

### Result

```
Voice envelope: Smooth curve showing formants (peaks)
                F1 ≈ 700 Hz
                F2 ≈ 1200 Hz  
                F3 ≈ 2500 Hz
```

## 3. Temporal Envelope (Attack/Release)

### Why the Time Axis Matters

Frequency smoothing removes pitch information, but it is symmetric: it treats rising energy and falling energy identically. Human speech is not symmetric. Consonants like "t", "k", and "p" are brief bursts of energy that must rise fast, while vowels like "a" and "o" decay slowly. Symmetric smoothing blurs both equally, which reduces intelligibility.

### The Attack/Release Model

After frequency smoothing, each frequency bin is further smoothed across time using two separate coefficients:

```
If energy is rising  → use attack coefficient (high = fast)
If energy is falling → use release coefficient (low = slow)
```

This is a first-order IIR (Infinite Impulse Response) filter with asymmetric behavior:

```
smoothed[f, t] = (1 - coeff) * smoothed[f, t-1] + coeff * magnitude[f, t]

where coeff = attack  if magnitude[f, t] > smoothed[f, t-1]
              release  otherwise
```

### NumPy Vectorized Implementation

The time loop is unavoidable because each frame depends on the previous one. However, the loop over frequency bins is eliminated by processing all bins simultaneously at each time step:

```
For each time frame t:
    current[all_bins] = magnitude[:, t]
    coefficient[all_bins] = where(current > previous, attack, release)
    previous = (1 - coefficient) * previous + coefficient * current
    smoothed[:, t] = previous
```

This reduces the total iteration count from `frequency_bins × time_frames` to just `time_frames`, with all frequency arithmetic done in fast NumPy C code.

### Default Parameters

- **attack** = 0.3 — rises to about 95% of a step in ~9 frames
- **release** = 0.05 — falls to about 5% of a step in ~58 frames

Tuning guidance:
- Sound is clicky or harsh → lower the attack value (e.g. 0.1)
- Sound is mushy or washy → raise the attack or lower the release

## 4. Spectral Transfer

### Key Insight

The vocoder transforms the carrier spectrum:

```
Output = (Carrier / Carrier_envelope) × Voice_envelope
```

This achieves two things:
1. **Whitening**: Flatten carrier spectrum
2. **Scaling**: Apply voice envelope

### Step-by-step

#### Step 3a: Spectral Whitening

```
Whitened_carrier[k] = Carrier[k] / (Carrier_envelope[k] + ε)
```

Where `ε` is a small constant to avoid division by zero.

**Effect**: Removes carrier's original spectral character

```
Original carrier:   ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁  (colored)
                               ↓
Whitened:           ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃  (flat)
```

#### Step 3b: Envelope Scaling

```
Output[k] = Whitened_carrier[k] × Voice_envelope[k]
```

**Effect**: Apply voice's spectral character

```
Whitened carrier:   ▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃  (flat)
× Voice envelope:   ▁▂▃▅▆█▆▅▃▂▁       (voice shape)
                         ↓
Output magnitude:   ▁▂▃▅▆█▆▅▃▂▁       (voice on carrier)
```

### Phase Handling

The output **preserves the carrier's original phase**:

```
Output_phase[k,t] = Carrier_phase[k,t]  (NOT voice phase!)
```

**Why?**
- Carrier phase determines pitch and timing (perceptually important)
- Voice phase is less important for spectral character
- Using voice phase causes artifacts and phasiness

### Combined Output

```
Output[k,t] = |Output[k,t]| × e^(i*Carrier_phase[k,t])
            = (|Whitened_carrier[k]| × |Voice_envelope[k]|) 
              × e^(i*Carrier_phase[k,t])
```

## 5. STFT Synthesis

### Inverse FFT

Convert back to time domain using Inverse FFT (IFFT):

```
Frames (freq):  X₁[k] X₂[k] X₃[k] X₄[k]
                   ↓     ↓     ↓     ↓
IFFT:          x₁[n] x₂[n] x₃[n] x₄[n]
                   ↓     ↓     ↓     ↓
Overlap-add:   ├────┤
               │    ├────┤
               │    │    ├────┤
               │    │    │    ├────┤
               ↓    ↓    ↓    ↓
Output:        [continuous audio]
```

### Overlap-Add

With 75% frame overlap:

```
Frame window:  [----]
               [  ----]  (overlaps by 75%)
               [    ----]

Overlap-add:   Each sample is sum of contributions from
               up to 4 overlapping frames
```

**Important**: Using Hann windows ensures perfect reconstruction:
```
Σ(Hann[n + k×hop]) = 1.0  (for all n)
```

This means output sums to original amplitude.

### Reconstruction Quality

- No phase distortion (we preserved carrier phase)
- No aliasing (FFT size ≥ signal bandwidth)
- Smooth transitions (Hann window overlap)
- Artifact-free (mathematically sound)

## 6. Complete Algorithm

### Pseudocode

```python
def vocode(voice, carrier):
    # STFT Analysis
    voice_stft = []
    carrier_stft = []
    for t in range(num_frames):
        window = hann_window(fft_size)
        
        # Frame and window
        voice_frame = voice[t*hop:t*hop + fft_size] * window
        carrier_frame = carrier[t*hop:t*hop + fft_size] * window
        
        # FFT
        voice_stft.append(fft(voice_frame))
        carrier_stft.append(fft(carrier_frame))
    
    # Processing
    output_stft = []
    for t in range(num_frames):
        # Envelope extraction
        voice_mag = |voice_stft[t]|
        voice_env = gaussian_blur(voice_mag)
        
        carrier_mag = |carrier_stft[t]|
        carrier_env = gaussian_blur(carrier_mag)
        
        # Temporal envelope (attack/release across time)
        voice_env = apply_temporal_envelope(voice_env)
        
        # Spectral transfer
        carrier_whitened = carrier_mag / (carrier_env + eps)
        output_mag = carrier_whitened * voice_env
        
        # Preserve carrier phase
        output_phase = angle(carrier_stft[t])
        
        # Combine magnitude and phase
        output_stft.append(output_mag * e^(i*output_phase))
    
    # STFT Synthesis
    output_time = []
    for t in range(num_frames):
        frame = ifft(output_stft[t]).real
        output_time.append(frame)
    
    # Overlap-add
    return overlap_add(output_time, hop_size)
```

## Mathematical Formulation

### Per-Frame Transfer Function

For frame index `t` and frequency bin `k`:

```
H[k,t] = (|C[k,t]| / (E_C[k,t] + ε)) × E_V[k,t]
```

Where:
- `C[k,t]` = Carrier spectrum (complex)
- `E_C[k,t]` = Carrier envelope magnitude
- `E_V[k,t]` = Voice envelope magnitude
- `ε` = Small constant (typically 1e-10)

### Output Spectrum

```
Y[k,t] = H[k,t] × e^(i*∠C[k,t])
       = |H[k,t]| × e^(i*∠C[k,t])
```

### Energy Conservation

The vocoder preserves energy from the carrier:

```
∑|Y[k,t]|² ≈ ∑|C[k,t]|²  (approximately)
```

This is why output loudness scales with carrier loudness.

## Spectral Envelope Parameters

### Gaussian Smoothing

The Gaussian blur standard deviation affects envelope extraction:

**Current implementation**: σ ≈ 8-16 FFT bins

```
σ smaller (< 8):   More detail, sharpens formants
σ larger (> 16):   Smoother, blurs formants
```

### Frequency Smoothing Range

At 96 kHz with FFT size 4096:
```
Per bin: 23.4 Hz
σ = 10 bins ≈ 234 Hz smoothing
```

This is ideal for vowel formants which are typically:
- F1: 200-900 Hz (broad)
- F2: 700-2500 Hz (broad)
- F3: 1500-4000 Hz (broad)

## Algorithm Properties

### Strengths

✓ **Simple and efficient**: O(N log N) per frame using FFT
✓ **Preserves intelligibility**: Formants remain clear, consonant transients preserved by attack/release
✓ **Natural sounding**: Uses carrier phase (no phasiness)
✓ **Flexible**: Works with any voice and carrier
✓ **Scalable**: Can handle long audio files
✓ **Temporal dynamics**: Asymmetric attack/release captures speech's natural asymmetry in time

### Limitations

✗ **Time-frequency tradeoff**: Can't have both fine frequency and time resolution
✗ **Formant smearing**: Very short windows blur formants
✗ **Harmonic artifacts**: Very large windows create pre-echo
✗ **Pitch perception**: Depends on carrier pitch structure (works best with pitched carriers)

## Comparison to Other Vocoders

### Phase Vocoder
- Uses phase reconstruction instead of carrier phase
- Better for time-stretching, worse for cross-synthesis
- More complex algorithm

### Sinusoidal Model
- Models audio as sum of sinusoids
- Very high quality, computationally expensive
- Requires tracking harmonics

### Fixed-Band Vocoder
- Uses fixed number of bands (e.g., 10-20)
- Simpler, works real-time
- Artifacts visible at band edges

### This Vocoder (Continuous Spectral)
- Uses full spectrum (continuous smoothing)
- Good quality, efficient
- Better formant capture than fixed-band

## Extending the Algorithm

### Potential Improvements

1. **Adaptive smoothing**: Vary σ based on signal content
2. **Harmonic extraction**: Isolate and preserve harmonics
3. **Time warping**: Non-linear time alignment
4. **Spectral morphing**: Blend between envelopes
5. **Multi-band**: Separate processing per frequency range
6. **Configurable attack/release**: Expose attack and release as user-facing configuration options

### Research Directions

- Machine learning for formant detection
- Real-time streaming implementation
- GPU acceleration for batch processing
- Psychoacoustic perceptual weighting

## References and Further Reading

### FFT and STFT
- Oppenheim & Schafer, "Discrete-Time Signal Processing"
- Smith, "STFT and Spectral Processing"

### Audio DSP
- Roads, "The Computer Music Tutorial"
- Lerch, "An Introduction to Audio Content Analysis"

### Vocoder Algorithms
- Laroche & Dolson, "New Phase-Vocoder Techniques for Real-Time Pitch Shifting"
- Flanagan & Golden, "Phase Vocoder"
- Ellis, "Spectral Envelope Tracking"

---

**Want to understand the design philosophy?** See [Design Philosophy](index.md).

**Ready to use the algorithm?** Check [Quick Start](../docs/02-quick-start.md) or [Advanced Usage](../docs/06-advanced-usage.md).
