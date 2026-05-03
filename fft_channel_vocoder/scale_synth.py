import numpy as np
from .config import sample_rate
from .pitch_corrector import PitchCorrector, midi_note_to_frequency
from .buffers import Carrier_Buffer
from . import clean_audio

window_size = 2**13
hop_size = window_size // 8


def build_note_schedule_from_frames(
    frames_and_notes, hop_size, sample_rate, total_duration_seconds
):
    """Convert frame-by-frame notes into a continuous note schedule.

    Args:
        frames_and_notes: List of (frame_index, note_class, octave) tuples.
        hop_size: Samples between frame boundaries.
        sample_rate: Sample rate in Hz.
        total_duration_seconds: Total duration of audio in seconds.

    Returns:
        List of {"note_class": str, "octave": int, "start": float, "end": float}.
    """
    if not frames_and_notes:
        return []

    schedule = []
    current_note_data = None
    start_frame = 0

    for frame_idx, note_class, octave in frames_and_notes:
        if current_note_data is None:
            current_note_data = (note_class, octave)
            start_frame = frame_idx
        elif (note_class, octave) != current_note_data:
            start_time = start_frame * hop_size / sample_rate
            end_time = frame_idx * hop_size / sample_rate
            schedule.append(
                {
                    "note_class": current_note_data[0],
                    "octave": current_note_data[1],
                    "start": start_time,
                    "end": end_time,
                }
            )
            current_note_data = (note_class, octave)
            start_frame = frame_idx

    if current_note_data is not None:
        start_time = start_frame * hop_size / sample_rate
        end_time = total_duration_seconds
        schedule.append(
            {
                "note_class": current_note_data[0],
                "octave": current_note_data[1],
                "start": start_time,
                "end": end_time,
            }
        )

    return schedule


def note_class_and_octave_to_frequency(note_class, octave):
    """Convert note class and octave to frequency in Hz."""
    note_index = [
        "c",
        "c#",
        "d",
        "d#",
        "e",
        "f",
        "f#",
        "g",
        "g#",
        "a",
        "a#",
        "b",
    ].index(note_class.lower())
    midi_note = octave * 12 + note_index
    return midi_note_to_frequency(midi_note)


def synthesize_pitch_corrected_carrier(
    voice_data,
    scale_notes,
    noise_gate_threshold_db=-40,
    min_frequency=50,
    max_frequency=500,
):
    """Synthesize carrier wave by detecting pitch from voice and snapping to scale.

    Args:
        voice_data: Voice audio as 1D numpy array.
        scale_notes: List of note class strings (e.g., ["c", "d", "e"]).
        noise_gate_threshold_db: Noise gate threshold in dB (default -40).
        min_frequency: Minimum frequency to detect (Hz, default 50).
        max_frequency: Maximum frequency to detect (Hz, default 500).

    Returns:
        Carrier wave as 1D numpy array, same length as voice_data.
    """
    print("Initializing pitch corrector")
    corrector = PitchCorrector(
        scale_notes,
        noise_gate_threshold_db,
        min_frequency=min_frequency,
        max_frequency=max_frequency,
    )
    corrector.update_peak(voice_data)

    total_duration = len(voice_data) / sample_rate
    print(f"Processing voice for pitch detection (duration: {total_duration:.2f}s)")

    frames_and_notes = []
    frame_idx = 0

    for start_sample in range(0, len(voice_data), hop_size):
        end_sample = min(start_sample + window_size, len(voice_data))
        frame = voice_data[start_sample:end_sample]

        result = corrector.process_frame(frame)
        if result is not None:
            note_class, octave = result
            frames_and_notes.append((frame_idx, note_class, octave))

        frame_idx += 1

    schedule = build_note_schedule_from_frames(
        frames_and_notes, hop_size, sample_rate, total_duration
    )

    print(f"Detected {len(schedule)} note regions")
    print("Building carrier buffer")

    carrier_buffer = Carrier_Buffer(total_duration)

    for note_info in schedule:
        frequency = note_class_and_octave_to_frequency(
            note_info["note_class"], note_info["octave"]
        )
        carrier_buffer.add_wave(note_info["start"], note_info["end"], frequency)

    print("Cleanup")
    carrier = carrier_buffer.carrier
    return clean_audio.clean(carrier)
