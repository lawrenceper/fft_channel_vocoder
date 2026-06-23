# sfz_instrument.py

# Builds a vocoded SFZ instrument by running the vocoder across all 128 MIDI notes.

from pathlib import Path
from .buffers import Carrier_Buffer
from .midi_synth import midi_note_to_frequency
from . import fft
from . import clean_io
from . import sfz


def build_note_carrier(frequency, duration_seconds):
    """Create a carrier wave filled with one frequency.

    Args:
        frequency: Pitch in Hz for the carrier.
        duration_seconds: Length of the carrier in seconds.

    Returns:
        1D float32 numpy array of the carrier wave.
    """
    carrier_buffer = Carrier_Buffer(duration_seconds)
    carrier_buffer.add_fill(frequency)
    return carrier_buffer.carrier


def build_vocoded_instrument(voice, output_path, duration_seconds=10.0):
    """creates a vocoded instrument based on your voice.
    Args:
        voice: 1D float32 numpy array of the modulator (voice) signal.
        output_path: Folder to write the note samples and SFZ file into.
        duration_seconds: Length of each generated note sample, in seconds.
    """
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    note_sample_pairs = []
    for midi_note in range(128):
        print(f"Vocoding note {midi_note}")
        frequency = midi_note_to_frequency(midi_note)
        carrier = build_note_carrier(frequency, duration_seconds)
        vocoded = fft.vocode(voice, carrier)

        sample_filename = f"note_{midi_note}.wav"
        clean_io.save(output_path / sample_filename, vocoded, convert_16bit=True)
        note_sample_pairs.append((midi_note, sample_filename))

    sfz.write_sfz(output_path / "instrument.sfz", note_sample_pairs)
