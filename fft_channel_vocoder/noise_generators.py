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
