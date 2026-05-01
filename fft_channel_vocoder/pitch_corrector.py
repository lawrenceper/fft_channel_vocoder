import numpy as np
from .config import sample_rate

NOTE_CLASSES = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]


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
        abs(midi_note_detected - midi_with_above)
    ]

    best_octave_idx = np.argmin(distances)
    if best_octave_idx == 0:
        return octave_below
    elif best_octave_idx == 2:
        return octave_above
    else:
        return octave


def detect_pitch(audio_frame, min_frequency=50, max_frequency=2000):
    """Detect pitch using autocorrelation-based method.

    Args:
        audio_frame: Audio samples (1D numpy array).
        min_frequency: Minimum frequency to search (Hz).
        max_frequency: Maximum frequency to search (Hz).

    Returns:
        Tuple of (frequency_hz, confidence) where confidence is in [0, 1].
        Returns (0, 0) if no pitch detected.
    """
    frame_length = len(audio_frame)
    if frame_length == 0:
        return (0, 0)

    min_period = int(sample_rate / max_frequency)
    max_period = int(sample_rate / min_frequency)

    if max_period >= frame_length or min_period <= 0:
        return (0, 0)

    autocorr = np.correlate(audio_frame, audio_frame, mode='full')
    autocorr = autocorr[len(autocorr) // 2:]
    autocorr = autocorr / (autocorr[0] + 1e-10)

    search_range = autocorr[min_period:max_period + 1]
    if len(search_range) == 0:
        return (0, 0)

    max_idx = np.argmax(search_range)
    period = min_period + max_idx

    confidence = search_range[max_idx] if len(search_range) > 0 else 0
    frequency = sample_rate / period if period > 0 else 0

    return (frequency, confidence)


class PitchCorrector:
    """Detects pitch from audio and corrects to a musical scale."""

    def __init__(self, scale_notes, noise_gate_threshold_db=-40):
        """Initialize pitch corrector.

        Args:
            scale_notes: List of note class strings (e.g., ["c", "d", "e"]).
            noise_gate_threshold_db: Gate threshold in dB relative to peak.
        """
        self.scale_notes = scale_notes
        self.noise_gate_threshold_db = noise_gate_threshold_db
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
            Tuple of (note_class, octave) or None if below noise gate.
        """
        frequency, confidence = detect_pitch(audio_frame)

        rms = np.sqrt(np.mean(audio_frame ** 2))
        amplitude_db = 20 * np.log10(rms / self.peak_amplitude + 1e-10)

        if amplitude_db < self.noise_gate_threshold_db or confidence < 0.1:
            return self.last_note

        note_class = frequency_to_note_class(frequency)
        snapped_note = snap_note_to_scale(note_class, self.scale_notes)

        if snapped_note is None:
            return self.last_note

        octave = determine_best_octave(frequency, snapped_note)
        self.last_note = (snapped_note, octave)
        return self.last_note
