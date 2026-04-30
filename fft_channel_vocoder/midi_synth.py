# midi_synth.py
import numpy as np
import mido
from .config import sample_rate
from . import clean_audio
from .buffers import Carrier_Buffer



def midi_note_to_frequency(note_number):
    """Convert MIDI note number to frequency in Hz."""
    return 440.0 * (2.0 ** ((note_number - 69) / 12.0))


def samples_from_duration(duration_seconds):
    """Calculate number of samples for a given duration."""
    return int(duration_seconds * sample_rate)


def merge_audio_tracks(tracks):
    """Sum multiple audio tracks, handling different lengths."""
    if not tracks:
        return np.array([], dtype=np.float32)
    max_length = max(len(track) for track in tracks)
    merged = np.zeros(max_length, dtype=np.float32)
    for track in tracks:
        merged[: len(track)] += track
    return merged


def extract_timing_events(midi_file_path):
    """Parse MIDI file and extract note on/off events with timestamps."""
    midi = mido.MidiFile(midi_file_path)
    # collect (abs_tick, track_index, msg) for all msgs
    all_msgs = []
    for ti, track in enumerate(midi.tracks):
        abs_tick = 0
        for msg in track:
            abs_tick += msg.time
            all_msgs.append((abs_tick, ti, msg))
    # sort by absolute tick to get global order
    all_msgs.sort(key=lambda x: x[0])
    events = []
    tempo = 500000  # default µs per beat
    last_tick = 0
    current_time = 0.0
    for abs_tick, _, msg in all_msgs:
        delta_ticks = abs_tick - last_tick
        # convert this delta in ticks to seconds using current tempo
        delta_seconds = mido.tick2second(delta_ticks, midi.ticks_per_beat, tempo)
        current_time += delta_seconds
        last_tick = abs_tick
        if msg.type == "set_tempo":
            tempo = msg.tempo
        if msg.type in ("note_on", "note_off"):
            events.append(
                {
                    "type": msg.type,
                    "note": getattr(msg, "note", None),
                    "velocity": getattr(msg, "velocity", 0),
                    "time": current_time,
                }
            )
    return events


def build_note_schedule(events):
    """Create a schedule of which notes are active at each time."""
    active_notes = {}
    schedule = []

    for event in events:
        note = event["note"]
        if event["type"] == "note_on" and event["velocity"] > 0:
            active_notes[note] = event["time"]
        elif event["type"] == "note_off" or (
            event["type"] == "note_on" and event["velocity"] == 0
        ):
            if note in active_notes:
                schedule.append(
                    {"note": note, "start": active_notes[note], "end": event["time"]}
                )
                del active_notes[note]
    return schedule


def generate_notes_layer(schedule, total_duration, carrier_buffer):
    """Generate audio for all notes in the schedule."""
    # Use one preallocated carrier buffer and write each note into it. Minimal pattern:

    for note in schedule:
        carrier_buffer.add_wave(
            note["start"],
            note["end"],
            midi_note_to_frequency(note["note"])
        )


def generate_noise_layer(silence_regions, total_duration, carrier_buffer):
    """Generate white noise for silence regions."""
    # Use one preallocated carrier buffer and write each note into it. Minimal pattern:
    for start, end in silence_regions:
        carrier_buffer.add_wave(start, end, 0)


def identify_silence_regions(schedule, total_duration):
    """Find time regions where no notes are playing."""
    if not schedule:
        return [(0.0, total_duration)]

    schedule_sorted = sorted(schedule, key=lambda x: x["start"])
    silence_regions = []
    current_time = 0.0

    for note in schedule_sorted:
        if note["start"] > current_time:
            silence_regions.append((current_time, note["start"]))
        current_time = max(current_time, note["end"])

    if current_time < total_duration:
        silence_regions.append((current_time, total_duration))

    return silence_regions


def calculate_total_duration(schedule):
    """Find the duration of the entire MIDI sequence."""
    if not schedule:
        return 0.0
    return max(note["end"] for note in schedule)


def synthesize_carrier_wave(midi_file_path):
    """Read MIDI file and generate carrier wave for vocoder."""
    print("Getting MIDI time events")
    events = extract_timing_events(midi_file_path)
    schedule = build_note_schedule(events)
    total_duration = calculate_total_duration(schedule)

    if total_duration == 0.0:
        return np.array([], dtype=np.float32)

    print("total_duration =", total_duration)
    total_samples = int(np.ceil(total_duration * sample_rate))
    print("total_samples =", total_samples)
    print("bytes_needed (approx) =", total_samples * 4, "bytes")

    carrier_buffer = Carrier_Buffer(total_duration)
    # silence_regions = identify_silence_regions(schedule, total_duration)
    generate_notes_layer(schedule, total_duration, carrier_buffer)
    # generate_noise_layer(silence_regions, total_duration, carrier_buffer)

    print("Cleanup")
    carrier = carrier_buffer.carrier
    return clean_audio.clean(carrier)
