# clean_io.py

# responsible for opening and saving files and passing them as Numpy arrays, and cleaning up audio as soon as files are opened and saved.

from .config import sample_rate
from . import clean_audio
import numpy as np
import soundfile as sf


def does_exist(filename):
    """Check whether a file exists on disk.

    Args:
        filename: Path-like or string path to check.

    Returns:
        True if the file can be opened for reading, False otherwise.
    """
    try:
        with open(filename, "r") as f:
            return True
    except:
        return False


def load(filename):
    """Load a WAV file and return a cleaned mono float32 array.

    Resamples to the project sample rate if needed and runs the full
    clean_audio pipeline.

    Args:
        filename: Path-like or string path to a WAV file.

    Returns:
        1D float32 numpy array normalised to [-1.0, 1.0].
    """
    #  Load the wav files
    audio, file_sample_rate = sf.read(filename)

    # Clean audio
    return clean_audio.clean(audio, file_sample_rate)


def save(filename, audio, convert_16bit=False):
    """Clean and write audio to a WAV file at the project sample rate.

    Args:
        filename: Destination path for the WAV file.
        audio: Numpy array of audio samples to save. May be mono or stereo.
        convert_16bit: When True, save as 16 bit integer instead of 32 bit
            float.
    """
    # Cleanup
    new_audio = clean_audio.clean(
        audio, skip_mono_conversion=True, convert_16bit=convert_16bit
    )

    # Save to file
    subtype = "PCM_16" if convert_16bit else "FLOAT"
    sf.write(filename, new_audio, sample_rate, subtype=subtype)
