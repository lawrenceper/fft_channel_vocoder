# clean_io.py

# responsible for opening and saving files and passing them as Numpy arrays, and cleaning up audio as soon as files are opened and saved.

from .config import sample_rate
from . import clean_audio
import numpy as np
from scipy.io import wavfile

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
    file_sample_rate, audio = wavfile.read(filename)

    # Clean audio
    return clean_audio.clean(audio, file_sample_rate)

def save(filename, audio):
    """Clean and write audio to a WAV file at the project sample rate.

    Args:
        filename: Destination path for the WAV file.
        audio: Numpy array of audio samples to save. May be mono or stereo.
    """
    # Cleanup
    new_audio = clean_audio.clean(audio, skip_mono_conversion=True)

    # Save to file
    wavfile.write(filename, sample_rate, new_audio.astype(np.float32))

