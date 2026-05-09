# clean_audio.py

# Organized audio pypeline for Vocoder
# handles the heavy DSP work before applying FFT vocoder, when loading and saving files.

# Source of truth
from .config import sample_rate

# import other libraries
import numpy as np
from math import gcd
from scipy.signal import resample_poly, butter, sosfilt


def make_stereo(left, right):
    """
    Validates two audio arrays and combines them into a stereo array.
    Assumes audio_check(array, skip_mono_check) is already defined.
    """
    # Validate both arrays using your check function
    # Ensuring skip_mono_check is False as requested
    audio_check(left, skip_mono_check=False)
    audio_check(right, skip_mono_check=False)

    # Check if they are the same length before stacking
    if left.shape != right.shape:
        raise ValueError(
            f"Arrays must have the same shape. Got {a.shape} and {b.shape}"
        )

    # Stack arrays along a new axis to create (samples, 2)
    # np.stack(..., axis=-1) is standard for interleaved stereo
    stereo_audio = np.column_stack((left, right))

    return stereo_audio


def resample(audio, current_sample_rate, target_sample_rate=None):
    """Resample audio to the target sample rate using polyphase filtering.

    Args:
        audio: Numpy array of audio samples.
        current_sample_rate: The sample rate of the input audio in Hz.
        target_sample_rate: Destination sample rate in Hz. Defaults to the
            project sample rate when not provided.

    Returns:
        Numpy array resampled to target_sample_rate, or the original array
        unchanged if the rates already match.
    """
    if target_sample_rate is None:
        target_sample_rate = sample_rate

    if current_sample_rate == target_sample_rate:
        return audio

    greatest_common_divisor = gcd(current_sample_rate, target_sample_rate)
    up = target_sample_rate // greatest_common_divisor
    down = current_sample_rate // greatest_common_divisor
    return resample_poly(audio, up, down)


def make_mono(audio):
    """Convert a multi-channel audio array to mono by averaging channels.

    Args:
        audio: Numpy array of shape (samples,) or (samples, channels).

    Returns:
        1D numpy array. Already-mono input is returned unchanged.
    """
    if len(audio.shape) > 1:
        return np.mean(audio, axis=1)
    else:
        return audio


def convert_float32(audio):
    """Convert an audio array to float32.

    int16 input is scaled to the [-1.0, 1.0] range. Any other dtype is cast
    directly to float32 without rescaling.

    Args:
        audio: Numpy array of audio samples.

    Returns:
        float32 numpy array.
    """
    if audio.dtype == np.int16:
        return audio.astype(np.float32) / 32768.0
    return audio.astype(np.float32)


def normalise(audio):
    """Normalise audio so the peak absolute value is 1.0.

    Args:
        audio: Numpy array of audio samples.

    Returns:
        Numpy array scaled so the loudest sample has magnitude 1.0.
    """
    # We use a small epsilon to avoid division by zero
    norm_factor = np.max(np.abs(audio)) + 1e-9
    return audio / norm_factor


# Safety check - ensure audio is valid before processing


def audio_check(audio, skip_mono_check=True):
    """Validate that audio is a non-empty numpy array.

    Args:
        audio: The value to validate.
        skip_mono_check: When False, also assert the array is 1D (mono).

    Raises:
        TypeError: If audio is not a numpy array.
        ValueError: If audio is not mono (when skip_mono_check is False) or is empty.
    """
    if not isinstance(audio, np.ndarray):
        raise TypeError(f"voice must be np.ndarray, got {type(audio)}")

    if not skip_mono_check and audio.ndim != 1:
        raise ValueError("Audio must be mono (1D arrays)")

    if len(audio) == 0:
        raise ValueError("Empty audio passed to vocoder")


def highpass(audio, cutoff_frequency):
    """Apply a 4th-order Butterworth high-pass filter to an audio array.

    Args:
        audio: 1D float32 numpy array of audio samples.
        cutoff_frequency: The -3 dB cutoff frequency in Hz.

    Returns:
        Filtered numpy array of the same shape and dtype.
    """
    second_order_sections = butter(
        4, cutoff_frequency, btype="high", fs=sample_rate, output="sos"
    )
    return sosfilt(second_order_sections, audio).astype(audio.dtype)


def lowpass(audio, cutoff_frequency):
    """Apply a 4th-order Butterworth low-pass filter to an audio array.

    Args:
        audio: 1D float32 numpy array of audio samples.
        cutoff_frequency: The -3 dB cutoff frequency in Hz.

    Returns:
        Filtered numpy array of the same shape and dtype.
    """
    second_order_sections = butter(
        4, cutoff_frequency, btype="low", fs=sample_rate, output="sos"
    )
    return sosfilt(second_order_sections, audio).astype(audio.dtype)


def clean(audio, current_sample_rate=None, skip_mono_conversion=False):
    """Normalise and prepare an audio array for processing or saving.

    Runs in order: validate → resample → make mono → convert to float32 →
    normalise. Resampling is skipped when current_sample_rate is None or
    already matches the project rate.

    Args:
        audio: Numpy array of audio samples.
        current_sample_rate: Sample rate of the input audio in Hz, or None to
            skip resampling.
        skip_mono_conversion: When True, skip the make_mono step (needed when
            saving stereo output).

    Returns:
        Cleaned float32 numpy array ready for processing or writing to disk.
    """
    # safety checks
    audio_check(audio)
    # If the synth returned an empty list or array, stop here
    if audio is None or len(audio) == 0:
        print(
            "Warning: Received empty audio buffer in clean(). Returning silent array."
        )
        return np.zeros(1024, dtype=np.float32)  # Return a small slice of silence

    # Change the sample rate if file_sample_rate is supplied
    # print("Fixing audio.")
    if current_sample_rate is not None and current_sample_rate != sample_rate:
        new_audio = resample(audio, current_sample_rate)  # Avoid forshadowing
    else:
        new_audio = audio
    # Make the track Mono
    if not skip_mono_conversion:
        new_audio = make_mono(new_audio)
    # Convert to float 32
    new_audio = convert_float32(new_audio)
    # Convert to Mono
    new_audio = normalise(new_audio)
    return new_audio
