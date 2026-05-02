# buffers.py

# holds a carrier buffer and synthesizer generators for MIDI and other purposes

import numpy as np
from .config import sample_rate


class Carrier_Buffer:
    """Pre-allocated audio buffer for building a carrier wave from note events."""

    def __init__(self, total_duration):
        """Allocate a silent buffer sized for the full duration.

        Args:
            total_duration: Length of the audio in seconds.
        """
        self.total_samples = int(np.ceil(total_duration * sample_rate))
        self.carrier = np.zeros(self.total_samples, dtype=np.float32)

    def add_wave(self, start_seconds, end_seconds, frequency):
        """Mix a wave into the buffer over a time range.

        Uses white noise for frequency <= 0 (silent/rest regions) and a
        sawtooth wave otherwise.

        Args:
            start_seconds: Start time of the note in seconds.
            end_seconds: End time of the note in seconds.
            frequency: Pitch in Hz. Pass 0 or negative to write white noise.
        """
        # Safety check:
        # Check if start is less than duration, and
        # end is capped to the length if end_seconds is longer than duration.
        start = int(round(start_seconds * sample_rate))
        if start > self.total_samples:
            raise ValueError("Start must be before duration")
        end = min(int(round(end_seconds * sample_rate)), self.total_samples)
        n = end - start
        if n <= 0:
            return
        if frequency <= 0:
            # Add white noise
            self.carrier[start:end] += self.white_noise(n)
        else:
            # Append a wave with the frequency
            self.carrier[start:end] += self.sawtooth_wave(frequency, n)


    def sawtooth_wave(self, frequency, num_samples):
        """Generate a sawtooth wave at the given frequency.

        Args:
            frequency: Pitch of the wave in Hz.
            num_samples: Number of samples to generate.

        Returns:
            1D float32 numpy array of the sawtooth waveform in the range [-1, 1].
        """
        indices = np.arange(num_samples)
        # Calculates phase from 0 to 1
        phase = (frequency * indices / sample_rate) % 1.0
        waveform = 2.0 * phase - 1.0
        return waveform.astype(np.float32)


    def white_noise(self, num_samples):
        """Generate white noise."""
        return np.random.uniform(-1.0, 1.0, num_samples).astype(np.float32)

