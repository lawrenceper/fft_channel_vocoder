# main.py

# This is where all the majic happens.
# This does the automation of opening a file, generating new sound, processing with the vocoder, and saving.

from pathlib import Path
from . import fft
from . import clean_audio
from . import clean_io
from . import midi_synth
from . import scale_synth
from .noise_generators import white_noise

def files_exist(path, name, extension):
    """
    Generator that iterates through all possible files that exist
    Args:
        path: The path to search for the files
        name, the name of the file
        extension, the extension of the file
    Yields:
        path+name+int+extention
    """
    path = Path(path)
    i = 1

    while True:
        suffix = f"{name}{i if i else ''}.{extension}"
        filepath = path / suffix

        if not clean_io.does_exist(filepath):
            break

        yield (filepath, f"{name}{i if i else ''}")
        i += 1

def load_scale(scale_file):
    """Load scale notes and parameters from a text file.

    Args:
        scale_file: Path to scale file.

    Returns:
        Tuple of (notes_list, parameters_dict) where parameters_dict contains
        optional min_freq and max_freq (Hz). Returns defaults for missing params.
    """
    notes = []
    params = {'min_freq': 50, 'max_freq': 500}

    with open(scale_file, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip().lower()
                try:
                    if key == 'min_freq':
                        params['min_freq'] = float(value.strip())
                    elif key == 'max_freq':
                        params['max_freq'] = float(value.strip())
                except ValueError:
                    pass
            else:
                notes.append(line.lower())

    return notes, params


def whisper(data):
    """
    Generates white noise data and vocodes
    """
    noise = white_noise(len(data))
    return fft.vocode(data, noise)



def main():
    """Run the full vocoder pipeline: load → generate → vocode → save."""

    input_path = Path("input")
    output_path = Path("output")

    # Loop through all voices
    for voice_file, voice_name in files_exist(input_path, "voice", "wav"):
        print(f"Loading audio from {voice_file.name}")
        voice_data = clean_io.load(voice_file)

        # Get all MIDI files
        for midi_file, midi_name in files_exist(input_path, "melody", "mid"):
            print(f"Getting carier wave from {midi_file.name}")
            carrier_data = midi_synth.synthesize_carrier_wave(midi_file)
            print("Applying vocoder")
            output_data = fft.vocode(voice_data, carrier_data)
            clean_io.save(output_path / f"{voice_name}_{midi_name}.wav", output_data)

        # Get all synth wave files
        for synth_file, synth_name in files_exist(input_path, "synth", "wav"):
            print(f"Loading carrier wave from {synth_file.name}")
            carrier_data = clean_io.load(synth_file)
            print("Applying vocoder")
            output_data = fft.vocode(voice_data, carrier_data)
            clean_io.save(output_path / f"{voice_name}_{synth_name}.wav", output_data)

        # Get all scale files for pitch correction
        for scale_file, scale_name in files_exist(input_path, "scale", "txt"):
            print(f"Loading scale from {scale_file.name}")
            scale_notes, scale_params = load_scale(scale_file)
            print("Detecting pitch and correcting to scale")
            carrier_data = scale_synth.synthesize_pitch_corrected_carrier(
                voice_data, scale_notes, noise_gate_threshold_db=-40,
                min_frequency=scale_params['min_freq'],
                max_frequency=scale_params['max_freq']
            )
            print("Applying vocoder")
            output_data = fft.vocode(voice_data, carrier_data)
            clean_io.save(output_path / f"{voice_name}_{scale_name}.wav", output_data)

        # Generate whisper track and save
        print("Generating stereo whisper track")
        stereo_whisper = clean_audio.make_stereo(
            whisper(voice_data),
            whisper(voice_data)
        )
        print("Saving stereo pair")
        clean_io.save(output_path / f"{voice_name}_whisper.wav", stereo_whisper)


if __name__ == "__main__":
    main()