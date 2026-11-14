import numpy as np
import pytest

from fft_channel_vocoder import fft as vocoder_fft
from fft_channel_vocoder import clean_audio


def _random_audio(num_samples, seed=0):
    rng = np.random.default_rng(seed)
    return rng.standard_normal(num_samples).astype(np.float32)


def test_trim_truncates_to_shortest_length():
    voice = _random_audio(100)
    carrier = _random_audio(50)
    trimmed_voice, trimmed_carrier = vocoder_fft.trim(voice, carrier)
    assert len(trimmed_voice) == 50
    assert len(trimmed_carrier) == 50


def test_vocode_rejects_non_mono_input():
    stereo = np.zeros((1000, 2), dtype=np.float32)
    mono = _random_audio(1000)
    with pytest.raises(ValueError):
        vocoder_fft.vocode(stereo, mono)


def test_vocode_rejects_empty_input():
    with pytest.raises(ValueError):
        vocoder_fft.vocode(np.array([], dtype=np.float32), _random_audio(1000))


def test_vocode_produces_finite_audio_of_similar_length():
    voice = _random_audio(9600, seed=1)
    carrier = _random_audio(9600, seed=2)
    output = vocoder_fft.vocode(voice, carrier)
    assert np.all(np.isfinite(output))
    # istft reconstruction length is close to, but not exactly, the input length.
    assert abs(len(output) - len(voice)) < vocoder_fft.fft_size


def test_vocode_output_can_be_cleaned_to_normalised_float32():
    voice = _random_audio(9600, seed=3)
    carrier = _random_audio(9600, seed=4)
    output = vocoder_fft.vocode(voice, carrier)
    cleaned = clean_audio.clean(output)
    assert cleaned.dtype == np.float32
    assert np.max(np.abs(cleaned)) == pytest.approx(1.0, abs=1e-5)


def test_process_fft_output_matches_voice_and_carrier_shape():
    voice_mag = np.abs(_random_audio(2048 * 3).reshape(-1, 3)) + 0.1
    carrier_mag = np.abs(_random_audio(2048 * 3).reshape(-1, 3)) + 0.1
    output_mag = vocoder_fft.process_fft(voice_mag, carrier_mag)
    assert output_mag.shape == voice_mag.shape
    assert np.all(np.isfinite(output_mag))
