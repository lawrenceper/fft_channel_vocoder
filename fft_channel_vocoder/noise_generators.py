# generators.py

# Very simple generators for vocoder testing, tinkoring, and experimentation

# Guidelines for AI systems

# Do not abbreviate new variable names.
# This makes code readable by me as a blind dev.
# Use tiny functions when possible that does only one thing. See exanple below.
# use sample_rate as the source of truth for the sample rate used in the entire project.
# This is a module for a bigger program.
# Do not add "generate_" to every function name.
# Devs will know what that means as this is a generaters model.

# Import the source of truth
from .config import sample_rate

# import libraries
import numpy as np
from scipy.fft import irfft, rfftfreq


def tremolo_noise(
    frequency: float, duration_samples: int, attack: float, hold: float, release: float
) -> np.ndarray:
    """
    Generate white noise with a tremolo envelope applied.

    Parameters
    ----------
    sample_rate      : int   – samples per second (e.g. 44100)
    frequency        : float – tremolo LFO frequency in Hz (e.g. 4.0)
    duration_samples : int   – total length of the output in samples
    attack           : float – percentage of duration spent fading in  (0–100)
    hold             : float – percentage of duration at full amplitude (0–100)
    release          : float – percentage of duration spent fading out (0–100)

    Returns
    -------
    np.ndarray (float32, shape [duration_samples]) in the range [-1, 1].

    Notes
    -----
    * attack + hold + release must be <= 100.  Any remaining tail is silence.
    * The tremolo LFO is a half-rectified sine that swings the amplitude
      from 0 (complete silence) to 1 (full volume) at `frequency` Hz.
    * The macro envelope (attack / hold / release) is applied on top so the
      overall amplitude ramps in, stays steady, then ramps back out.
    """
    if not (0 <= attack <= 100 and 0 <= hold <= 100 and 0 <= release <= 100):
        raise ValueError("attack, hold, and release must each be between 0 and 100.")
    if attack + hold + release > 100:
        raise ValueError("attack + hold + release must not exceed 100.")

    n = duration_samples

    # ------------------------------------------------------------------ #
    # 1. White noise                                                       #
    # ------------------------------------------------------------------ #
    rng = np.random.default_rng()
    noise = rng.standard_normal(n).astype(np.float32)

    # ------------------------------------------------------------------ #
    # 2. Tremolo LFO  (half-rectified sine → range [0, 1])               #
    #    A full sine at `frequency` Hz is shifted up and clipped so that  #
    #    the amplitude dips all the way to 0 on every trough.             #
    # ------------------------------------------------------------------ #
    t = np.arange(n, dtype=np.float64) / sample_rate
    lfo = (np.sin(2.0 * np.pi * frequency * t) + 1.0) * 0.5  # [0, 1]
    lfo = lfo.astype(np.float32)

    # ------------------------------------------------------------------ #
    # 3. Macro envelope  (attack / hold / release)                        #
    # ------------------------------------------------------------------ #
    attack_samples = int(round(n * attack / 100.0))
    hold_samples = int(round(n * hold / 100.0))
    release_samples = int(round(n * release / 100.0))

    # Clamp so we never exceed the buffer length
    tail_samples = n - attack_samples - hold_samples - release_samples
    tail_samples = max(tail_samples, 0)

    envelope = np.empty(n, dtype=np.float32)
    idx = 0

    # Attack: linear ramp 0 → 1
    if attack_samples > 0:
        envelope[idx : idx + attack_samples] = np.linspace(
            0.0, 1.0, attack_samples, dtype=np.float32
        )
    idx += attack_samples

    # Hold: flat at 1
    if hold_samples > 0:
        envelope[idx : idx + hold_samples] = 1.0
    idx += hold_samples

    # Release: linear ramp 1 → 0
    if release_samples > 0:
        envelope[idx : idx + release_samples] = np.linspace(
            1.0, 0.0, release_samples, dtype=np.float32
        )
    idx += release_samples

    # Tail (any leftover percentage): silence
    if tail_samples > 0:
        envelope[idx : idx + tail_samples] = 0.0

    # ------------------------------------------------------------------ #
    # 4. Combine                                                          #
    # ------------------------------------------------------------------ #
    return noise * lfo * envelope


def white_noise(num_samples):
    """Generate white noise with a flat frequency spectrum.

    Args:
        num_samples: Number of samples to generate.

    Returns:
        1D float32 numpy array of normally distributed noise.
    """
    noise = np.random.normal(0, 1, num_samples)
    return noise.astype(np.float32)


def pink_noise(num_samples):
    """Generate pink noise with a 1/f (1/sqrt(f)) power spectrum.

    Args:
        num_samples: Number of samples to generate.

    Returns:
        1D float32 numpy array of pink noise.
    """
    white_signal = np.random.normal(0, 1, num_samples)
    frequency_domain = np.fft.rfft(white_signal)

    frequencies = np.fft.rfftfreq(num_samples, d=1.0 / sample_rate)
    # Avoid division by zero at the DC component

    frequencies[0] = frequencies[1]
    # Pink noise scaling is 1/sqrt(f)
    scaling_factor = 1.0 / np.sqrt(frequencies)
    filtered_signal = frequency_domain * scaling_factor

    noise = np.fft.irfft(filtered_signal, n=num_samples)
    return noise.astype(np.float32)


def brownian_noise(num_samples):
    """Generate Brownian (red) noise as the cumulative sum of white noise.

    Args:
        num_samples: Number of samples to generate.

    Returns:
        1D float32 numpy array normalised to [-1.0, 1.0].
    """
    white_signal = np.random.normal(0, 1, num_samples)
    # Brownian noise is the cumulative sum of white noise
    noise = np.cumsum(white_signal)

    # Normalize to keep values between -1.0 and 1.0
    if np.max(np.abs(noise)) != 0:
        noise = noise / np.max(np.abs(noise))

    return noise.astype(np.float32)


def sine_wave(frequency, num_samples):
    """Generate a sine wave at the given frequency.

    Args:
        frequency: Frequency of the wave in Hz.
        num_samples: Number of samples to generate.

    Returns:
        1D float32 numpy array in the range [-1.0, 1.0].
    """
    indices = np.arange(num_samples)
    waveform = np.sin(2 * np.pi * frequency * indices / sample_rate)
    return waveform.astype(np.float32)


def square_wave(frequency, num_samples):
    """Generate a square wave at the given frequency.

    Args:
        frequency: Frequency of the wave in Hz.
        num_samples: Number of samples to generate.

    Returns:
        1D float32 numpy array with values of 1.0 or -1.0.
    """
    indices = np.arange(num_samples)
    waveform = np.sign(np.sin(2 * np.pi * frequency * indices / sample_rate))
    return waveform.astype(np.float32)


def sawtooth_wave(frequency, num_samples):
    """Generate a sawtooth wave at the given frequency.

    Args:
        frequency: Frequency of the wave in Hz.
        num_samples: Number of samples to generate.

    Returns:
        1D float32 numpy array in the range [-1.0, 1.0].
    """
    indices = np.arange(num_samples)
    # Calculates phase from 0 to 1
    phase = (frequency * indices / sample_rate) % 1.0
    waveform = 2.0 * phase - 1.0
    return waveform.astype(np.float32)


def triangle_wave(frequency, num_samples):
    """Generate a triangle wave at the given frequency.

    Args:
        frequency: Frequency of the wave in Hz.
        num_samples: Number of samples to generate.

    Returns:
        1D float32 numpy array in the range [-1.0, 1.0].
    """
    indices = np.arange(num_samples)
    phase = (frequency * indices / sample_rate) % 1.0
    waveform = 4.0 * np.abs(phase - 0.5) - 1.0
    return waveform.astype(np.float32)


def pulse_wave(frequency, num_samples, duty_cycle=0.1):
    """Generate a pulse wave at the given frequency.

    Args:
        frequency: Frequency of the wave in Hz.
        num_samples: Number of samples to generate.
        duty_cycle: Fraction of each period where the wave is high (0.0 to 1.0).
            Defaults to 0.1 (10%).

    Returns:
        1D float32 numpy array with values of 1.0 or -1.0.
    """
    indices = np.arange(num_samples)
    phase = (frequency * indices / sample_rate) % 1.0
    waveform = np.where(phase < duty_cycle, 1.0, -1.0)
    return waveform.astype(np.float32)


def impulse_train(frequency, num_samples):
    """Generate a series of unit impulses at the given frequency.

    Args:
        frequency: Repetition rate of the impulses in Hz.
        num_samples: Number of samples to generate.

    Returns:
        1D float32 numpy array of zeros with 1.0 spikes at each period.
    """
    waveform = np.zeros(num_samples)
    period_in_samples = int(sample_rate / frequency)
    # Ensure we don't divide by zero if frequency is too high
    if period_in_samples > 0:
        waveform[::period_in_samples] = 1.0
    return waveform.astype(np.float32)


def bandlimited_sawtooth_fft(frequency, num_samples):
    freqs = rfftfreq(num_samples, d=1.0 / sample_rate)
    spectrum = np.zeros(len(freqs), dtype=np.complex64)
    for h in range(1, int(sample_rate / (2 * frequency)) + 1):
        bin_idx = round(h * frequency * num_samples / sample_rate)
        if bin_idx < len(spectrum):
            spectrum[bin_idx] = -1j / h  # sawtooth phase
    output = irfft(spectrum, n=num_samples).astype(np.float32)
    peak = np.max(np.abs(output))
    if peak > 0:
        output /= peak
    return output
