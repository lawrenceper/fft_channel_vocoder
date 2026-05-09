import numpy as np
import librosa
from . import clean_audio
from .config import sample_rate
from .config import pitch_correct_fft_size as old_pitch_correct_fft_size
from .config import pitch_correcter_hop as old_pitch_correcter_hop

pitch_correct_fft_size = 2**old_pitch_correct_fft_size
pitch_correcter_hop = pitch_correct_fft_size // old_pitch_correcter_hop


NOTE_CLASSES = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]

PITCH_DETECT_SAMPLE_RATE = 16000


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


def downsample_for_pitch(audio):
    """Downsample audio from the project rate to the pitch detection rate."""
    return clean_audio.resample(audio, sample_rate, PITCH_DETECT_SAMPLE_RATE)


def detect_pitch(audio_16k, min_frequency=50, max_frequency=500):
    """Run pYIN on full 16 kHz audio, returning per-hop pitch arrays.

    Args:
        audio_16k: Audio at PITCH_DETECT_SAMPLE_RATE (1D float32 numpy array).
        min_frequency: Minimum frequency to search (Hz).
        max_frequency: Maximum frequency to search (Hz).

    Returns:
        Tuple of (frequencies, voiced_flags) — one value per pYIN hop.
    """
    frequencies, voiced_flags, _ = librosa.pyin(
        audio_16k.astype(np.float32),
        fmin=float(min_frequency),
        fmax=float(max_frequency),
        sr=PITCH_DETECT_SAMPLE_RATE,
        frame_length=pitch_correct_fft_size,
        hop_length=pitch_correcter_hop,
    )
    return frequencies, voiced_flags


class PitchCorrector:
    """Detects pitch from audio and corrects to a musical scale."""

    def __init__(
        self,
        scale_notes,
        noise_gate_threshold_db=-20,
        min_frequency=50,
        max_frequency=500,
    ):
        """Initialize pitch corrector.

        Args:
            scale_notes: List of note class strings (e.g., ["c", "d", "e"]).
            noise_gate_threshold_db: Gate threshold in dB relative to peak.
            min_frequency: Minimum frequency to detect (Hz, default 50).
            max_frequency: Maximum frequency to detect (Hz, default 500).
        """
        self.scale_notes = scale_notes
        self.noise_gate_threshold_db = noise_gate_threshold_db
        self.min_frequency = min_frequency
        self.max_frequency = max_frequency

    def _frame_to_note(self, freq, rms, peak_amplitude):
        """Convert a voiced frame to a snapped (note_class, octave) or None."""
        rms_db = 20 * np.log10(rms / peak_amplitude + 1e-10)
        if rms_db < self.noise_gate_threshold_db:
            return None
        note_class = frequency_to_note_class(freq)
        snapped = snap_note_to_scale(note_class, self.scale_notes)
        if snapped is None:
            return None
        return (snapped, determine_best_octave(freq, snapped))

    def process_audio(self, audio):
        """Detect and snap all pitched frames in a full audio array.

        Downsamples to 16 kHz, runs pYIN once on the whole signal, then
        applies the noise gate and scale snap to every voiced hop.

        Args:
            audio: Full voice audio at the project sample rate (1D numpy array).

        Returns:
            Tuple of (frames_and_notes, hop_length) where frames_and_notes is
            a list of (frame_idx, note_class, octave) and hop_length is the
            pYIN hop size in 16 kHz samples.
        """

        audio_16k = downsample_for_pitch(audio)
        frequencies, voiced_flags = detect_pitch(
            audio_16k, self.min_frequency, self.max_frequency
        )
        hop_rms = librosa.feature.rms(
            y=audio_16k,
            frame_length=PITCH_DETECT_FRAME_LENGTH,
            hop_length=hop_length,
        )[0]
        peak_amplitude = float(np.max(np.abs(audio_16k))) + 1e-6
        safe_length = min(len(voiced_flags), len(hop_rms))
        results = []
        for frame_idx in np.where(voiced_flags[:safe_length])[0]:
            freq = frequencies[frame_idx]
            if np.isnan(freq):
                continue
            note = self._frame_to_note(freq, hop_rms[frame_idx], peak_amplitude)
            if note is not None:
                results.append((int(frame_idx), note[0], note[1]))
        return results, pitch_correcter_hop
