import numpy as np
from .config import sample_rate

NOTE_CLASSES = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]


def measure_harmonic_strength(autocorr_array, period, num_cycles_check=4):
    """Measure harmonic structure strength via periodicity in autocorrelation.

    Voiced sounds create repeating periodic structure in autocorrelation.
    Unvoiced sounds (sibilants) show no periodicity—just noise.

    Args:
        autocorr_array: Normalized autocorrelation array from correlate().
        period: Detected period in samples (sample index, not lag).
        num_cycles_check: Number of harmonic cycles to analyze.

    Returns:
        Harmonic strength score in [0, 1]. High score = strong periodicity.
    """
    if period <= 0 or period * num_cycles_check >= len(autocorr_array):
        return 0.0

    fundamental_peak = autocorr_array[period]
    if fundamental_peak < 0.1:
        return 0.0

    cycle_peaks = []
    for cycle_num in range(1, num_cycles_check + 1):
        cycle_idx = period * cycle_num
        if cycle_idx >= len(autocorr_array):
            break
        peak_value = abs(autocorr_array[cycle_idx])
        cycle_peaks.append(peak_value)

    if not cycle_peaks:
        return 0.0

    cycle_peaks = np.array(cycle_peaks)
    decaying_pattern = np.any(cycle_peaks[1:] < cycle_peaks[:-1])

    mean_cycle_strength = np.mean(cycle_peaks)
    relative_strength = mean_cycle_strength / (fundamental_peak + 1e-10)

    harmonic_strength = relative_strength * (0.7 if decaying_pattern else 0.4)
    return min(1.0, max(0.0, harmonic_strength))


def frequency_to_midi_note(frequency):
    """Convert frequency in Hz to MIDI note number."""
    return 69 + 12 * np.log2(frequency / 440.0)


def midi_note_to_frequency(midi_note):
    """Convert MIDI note number to frequency in Hz."""
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))


def frequency_to_note_class(frequency):
    """Extract note class (c, c#, d, etc.) from frequency, ignoring octave."""
    midi_note = frequency_to_midi_note(frequency)
    note_index = int(round(midi_note)) % 12
    return NOTE_CLASSES[note_index]


def snap_note_to_scale(note_class, scale_notes):
    """Find nearest allowed note class in scale."""
    if note_class not in NOTE_CLASSES:
        return None

    note_index = NOTE_CLASSES.index(note_class)
    scale_indices = [NOTE_CLASSES.index(n) for n in scale_notes if n in NOTE_CLASSES]

    if not scale_indices:
        return None

    distances = [abs(note_index - scale_idx) for scale_idx in scale_indices]
    min_distance_idx = np.argmin(distances)
    return scale_notes[min_distance_idx]


def determine_best_octave(frequency, note_class):
    """Find octave that places note_class closest to original frequency."""
    midi_note_detected = frequency_to_midi_note(frequency)
    note_semitone = NOTE_CLASSES.index(note_class.lower())

    octave = int((midi_note_detected - note_semitone) / 12)
    midi_note_with_octave = octave * 12 + note_semitone

    octave_below = octave - 1
    octave_above = octave + 1

    midi_with_below = octave_below * 12 + note_semitone
    midi_with_above = octave_above * 12 + note_semitone

    distances = [
        abs(midi_note_detected - midi_with_below),
        abs(midi_note_detected - midi_note_with_octave),
        abs(midi_note_detected - midi_with_above),
    ]

    best_octave_idx = np.argmin(distances)
    if best_octave_idx == 0:
        return octave_below
    elif best_octave_idx == 2:
        return octave_above
    else:
        return octave


def compute_fft_autocorrelation(audio_frame):
    """Compute autocorrelation using FFT for O(n log n) performance.

    Args:
        audio_frame: Audio samples (1D numpy array).

    Returns:
        Normalized autocorrelation array.
    """
    frame_length = len(audio_frame)
    padded_length = 2 ** int(np.ceil(np.log2(2 * frame_length)))

    windowed_frame = audio_frame * np.hanning(frame_length)
    padded_frame = np.zeros(padded_length)
    padded_frame[:frame_length] = windowed_frame

    fft_result = np.fft.fft(padded_frame)
    power_spectrum = np.abs(fft_result) ** 2
    autocorr = np.fft.ifft(power_spectrum).real

    autocorr = autocorr[:frame_length]
    autocorr = autocorr / (autocorr[0] + 1e-10)

    return autocorr


def detect_pitch(audio_frame, min_frequency=50, max_frequency=500):
    """Detect pitch using autocorrelation-based method with harmonic verification.

    Args:
        audio_frame: Audio samples (1D numpy array).
        min_frequency: Minimum frequency to search (Hz).
        max_frequency: Maximum frequency to search (Hz).

    Returns:
        Tuple of (frequency_hz, confidence, harmonic_strength).
        Confidence and harmonic_strength are in [0, 1].
        Returns (0, 0, 0) if no pitch detected.
    """
    frame_length = len(audio_frame)
    if frame_length == 0:
        return (0, 0, 0)

    min_period = int(sample_rate / max_frequency)
    max_period = int(sample_rate / min_frequency)

    if max_period >= frame_length or min_period <= 0:
        return (0, 0, 0)

    autocorr = compute_fft_autocorrelation(audio_frame)

    search_range = autocorr[min_period : max_period + 1]
    if len(search_range) == 0:
        return (0, 0, 0)

    max_idx = np.argmax(search_range)
    period = min_period + max_idx

    confidence = search_range[max_idx] if len(search_range) > 0 else 0
    frequency = sample_rate / period if period > 0 else 0

    harmonic_strength = measure_harmonic_strength(autocorr, period, num_cycles_check=4)

    return (frequency, confidence, harmonic_strength)


class PitchCorrector:
    """Detects pitch from audio and corrects to a musical scale."""

    def __init__(
        self,
        scale_notes,
        noise_gate_threshold_db=-20,
        harmonic_strength_threshold=0.3,
        min_frequency=50,
        max_frequency=500,
    ):
        """Initialize pitch corrector.

        Args:
            scale_notes: List of note class strings (e.g., ["c", "d", "e"]).
            noise_gate_threshold_db: Gate threshold in dB relative to peak.
            harmonic_strength_threshold: Minimum harmonic strength (0-1) to accept pitch.
                Higher values reject more non-harmonic content (default 0.3 for balance).
            min_frequency: Minimum frequency to detect (Hz, default 50).
            max_frequency: Maximum frequency to detect (Hz, default 500).
        """
        self.scale_notes = scale_notes
        self.noise_gate_threshold_db = noise_gate_threshold_db
        self.harmonic_strength_threshold = harmonic_strength_threshold
        self.min_frequency = min_frequency
        self.max_frequency = max_frequency
        self.last_note = None
        self.peak_amplitude = 1e-6

    def update_peak(self, audio_data):
        """Update peak amplitude for noise gate calculation."""
        max_val = np.max(np.abs(audio_data))
        if max_val > self.peak_amplitude:
            self.peak_amplitude = max_val

    def process_frame(self, audio_frame):
        """Process one audio frame and return (note_class, octave) or None.

        Returns:
            Tuple of (note_class, octave) or None if below noise gate or harmonic threshold.
        """
        rms = np.sqrt(np.mean(audio_frame**2))
        amplitude_db = 20 * np.log10(rms / self.peak_amplitude + 1e-10)

        if amplitude_db < self.noise_gate_threshold_db:
            return self.last_note

        frequency, confidence, harmonic_strength = detect_pitch(
            audio_frame,
            min_frequency=self.min_frequency,
            max_frequency=self.max_frequency,
        )

        if confidence < 0.1:
            return self.last_note

        if harmonic_strength < self.harmonic_strength_threshold:
            return self.last_note

        note_class = frequency_to_note_class(frequency)
        snapped_note = snap_note_to_scale(note_class, self.scale_notes)

        if snapped_note is None:
            return self.last_note

        octave = determine_best_octave(frequency, snapped_note)
        self.last_note = (snapped_note, octave)
        return self.last_note
