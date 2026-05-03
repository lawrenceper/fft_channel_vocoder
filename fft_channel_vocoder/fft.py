from .config import sample_rate, vocoder_fft_size
import numpy as np
from scipy.signal import stft, istft
from scipy.ndimage import gaussian_filter1d
from . import clean_audio

fft_size = 2**vocoder_fft_size
hop = fft_size // 4


def get_stft(voice, carrier):
    """Compute the STFT of voice and carrier and extract magnitude and phase.

    Args:
        voice: 1D float32 numpy array of the modulator (voice) signal.
        carrier: 1D float32 numpy array of the carrier signal.

    Returns:
        Tuple of (voice_mag, carrier_mag, carrier_phase) where each is a 2D
        numpy array with shape (frequency_bins, time_frames).
    """
    # 1. Get STFT
    _, _, voice_stft = stft(
        voice, fs=sample_rate, nperseg=fft_size, noverlap=fft_size - hop
    )
    _, _, carrier_stft = stft(
        carrier, fs=sample_rate, nperseg=fft_size, noverlap=fft_size - hop
    )
    # Mag means magnitude
    voice_mag = np.abs(voice_stft)
    carrier_mag = np.abs(carrier_stft)
    carrier_phase = np.angle(carrier_stft)
    return (voice_mag, carrier_mag, carrier_phase)


def calculate_frequency_dependent_sigma(normalized_frequency):
    """Calculate sigma for a frequency using logarithmic scaling.

    Maps linear frequency to log space. Lower frequencies get higher sigma
    (removes pitch), higher frequencies get lower sigma (preserves detail).

    Args:
        normalized_frequency: Value from 0 (lowest freq) to 1 (highest freq).

    Returns:
        Sigma value for Gaussian smoothing.
    """
    sigma_low = 6.0
    sigma_high = 1.5
    # Map to log space: higher normalized_frequency = exponentially higher perceived pitch
    log_frequency = np.log1p(normalized_frequency * 10) / np.log1p(10)
    sigma = sigma_low + (sigma_high - sigma_low) * log_frequency
    return sigma


def apply_frequency_dependent_smoothing(magnitude_spectrum):
    """Smooth magnitude spectrum with smooth logarithmic sigma scaling.

    Applies a continuous curve of sigma values across the spectrum:
    low frequencies get aggressive smoothing (removes pitch leakage),
    high frequencies get light smoothing (preserves vocal character).

    Args:
        magnitude_spectrum: 2D numpy array of STFT magnitudes (frequency x time).

    Returns:
        2D numpy array of smoothed magnitudes.
    """
    num_frequency_bins = magnitude_spectrum.shape[0]
    smoothed = np.zeros_like(magnitude_spectrum)

    # Use many overlapping bands to create a smooth continuous transition
    num_bands = 15
    band_size = max(1, num_frequency_bins // num_bands)

    for band_idx in range(num_bands):
        start = band_idx * band_size
        end = min((band_idx + 1) * band_size, num_frequency_bins)
        if end <= start:
            break

        # Calculate center frequency of this band and get appropriate sigma
        band_center = (start + end) / 2
        normalized_frequency = band_center / num_frequency_bins
        sigma = calculate_frequency_dependent_sigma(normalized_frequency)

        # Smooth this band with its calculated sigma
        smoothed[start:end, :] = gaussian_filter1d(
            magnitude_spectrum[start:end, :], sigma=sigma, axis=0
        )

    return smoothed


def process_fft(voice_mag, carrier_mag):
    """Apply spectral envelope transfer from voice to carrier.

    Smooths both magnitude spectra to extract formant envelopes, then applies
    spectral whitening on the carrier before multiplying by the voice envelope.

    Args:
        voice_mag: 2D numpy array of voice STFT magnitudes (frequency x time).
        carrier_mag: 2D numpy array of carrier STFT magnitudes (frequency x time).

    Returns:
        2D numpy array of output magnitudes with the voice's spectral shape
        imposed on the carrier.
    """
    # 2. Spectral Smoothing with frequency-dependent sigma
    # Lower frequencies get more smoothing (removes pitch leakage)
    # Higher frequencies get less smoothing (preserves vocal character)
    voice_env = apply_frequency_dependent_smoothing(voice_mag)
    carrier_env = apply_frequency_dependent_smoothing(carrier_mag)

    # 3. Apply: (Synth / Synth_Env) * Voice_Env
    # The (carrier_mag / carrier_env) part is 'Spectral Whitening'
    carrier_white = carrier_mag / (carrier_env + 1e-6)
    output_mag = carrier_white * voice_env
    return output_mag


def reconstruct_fft(output_mag, carrier_phase):
    """Reconstruct a time-domain signal from magnitude and phase spectra.

    Args:
        output_mag: 2D numpy array of output magnitudes (frequency x time).
        carrier_phase: 2D numpy array of carrier phase angles (frequency x time).

    Returns:
        1D numpy array of the reconstructed time-domain audio signal.
    """
    # 4. Reconstruct
    Y = output_mag * np.exp(1j * carrier_phase)
    _, output = istft(Y, fs=sample_rate, nperseg=fft_size, noverlap=fft_size - hop)
    return output


def trim(voice, carrier):
    """Trim both arrays to the length of the shorter one.

    Args:
        voice: 1D numpy array of the voice signal.
        carrier: 1D numpy array of the carrier signal.

    Returns:
        Tuple of (voice, carrier) both truncated to the same length.
    """
    # Handle Length Discrepancy (Match to the shortest)
    min_length = min(len(voice), len(carrier))
    voice = voice[:min_length]
    carrier = carrier[:min_length]
    return (voice, carrier)


def vocode(voice, carrier):
    """Apply FFT vocoding: impose the voice's spectral envelope on the carrier.

    Args:
        voice: 1D float32 numpy array of the modulator (voice) signal.
        carrier: 1D float32 numpy array of the carrier signal.

    Returns:
        1D numpy array of the vocoded output signal.

    Raises:
        TypeError: If either argument is not a numpy array.
        ValueError: If either array is not mono or is empty.
    """
    # Safety check
    clean_audio.audio_check(voice, skip_mono_check=False)
    clean_audio.audio_check(carrier, skip_mono_check=False)
    # Trim the project before vocoding
    trimmed_voice, trimmed_carrier = trim(voice, carrier)

    # Get the STFTs used for vocoding
    voice_mag, carrier_mag, carrier_phase = get_stft(trimmed_voice, trimmed_carrier)

    # process the vocoder
    output_mag = process_fft(voice_mag, carrier_mag)

    # Reconstruct everything back together
    return reconstruct_fft(output_mag, carrier_phase)
