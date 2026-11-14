import numpy as np
import pytest

from fft_channel_vocoder import clean_audio


def test_make_mono_averages_channels():
    stereo = np.array([[1.0, -1.0], [0.5, -0.5]], dtype=np.float32)
    mono = clean_audio.make_mono(stereo)
    assert mono.shape == (2,)
    np.testing.assert_allclose(mono, [0.0, 0.0])


def test_make_mono_leaves_mono_input_unchanged():
    mono_in = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    assert clean_audio.make_mono(mono_in) is mono_in


def test_make_stereo_combines_matching_arrays():
    left = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    right = np.array([4.0, 5.0, 6.0], dtype=np.float32)
    stereo = clean_audio.make_stereo(left, right)
    assert stereo.shape == (3, 2)
    np.testing.assert_allclose(stereo[:, 0], left)
    np.testing.assert_allclose(stereo[:, 1], right)


def test_make_stereo_raises_value_error_on_shape_mismatch():
    left = np.zeros(5, dtype=np.float32)
    right = np.zeros(6, dtype=np.float32)
    with pytest.raises(ValueError, match="same shape"):
        clean_audio.make_stereo(left, right)


def test_convert_float32_scales_int16():
    audio = np.array([32767, -32768], dtype=np.int16)
    converted = clean_audio.convert_float32(audio)
    assert converted.dtype == np.float32
    assert converted[0] == pytest.approx(1.0, abs=1e-4)


def test_convert_int16_scales_float():
    audio = np.array([1.0, -1.0, 0.0], dtype=np.float32)
    converted = clean_audio.convert_int16(audio)
    assert converted.dtype == np.int16
    assert converted[0] == 32767
    assert converted[1] == -32767


def test_convert_int16_is_roundtrippable_with_convert_float32():
    audio = np.linspace(-1.0, 1.0, 100, dtype=np.float32)
    roundtripped = clean_audio.convert_float32(clean_audio.convert_int16(audio))
    np.testing.assert_allclose(roundtripped, audio, atol=1e-3)


def test_normalise_scales_peak_to_one():
    audio = np.array([0.1, -0.5, 0.25], dtype=np.float32)
    normalised = clean_audio.normalise(audio)
    assert np.max(np.abs(normalised)) == pytest.approx(1.0, abs=1e-6)


def test_normalise_handles_silence_without_dividing_by_zero():
    audio = np.zeros(10, dtype=np.float32)
    normalised = clean_audio.normalise(audio)
    assert np.all(np.isfinite(normalised))


def test_audio_check_rejects_non_ndarray():
    with pytest.raises(TypeError):
        clean_audio.audio_check([1, 2, 3])


def test_audio_check_rejects_empty_array():
    with pytest.raises(ValueError):
        clean_audio.audio_check(np.array([], dtype=np.float32))


def test_audio_check_rejects_stereo_when_mono_required():
    stereo = np.zeros((10, 2), dtype=np.float32)
    with pytest.raises(ValueError):
        clean_audio.audio_check(stereo, skip_mono_check=False)


def test_audio_check_allows_stereo_when_mono_not_required():
    stereo = np.zeros((10, 2), dtype=np.float32)
    clean_audio.audio_check(stereo, skip_mono_check=True)


def test_resample_returns_same_array_when_rates_match():
    audio = np.zeros(100, dtype=np.float32)
    result = clean_audio.resample(audio, 48000, 48000)
    assert result is audio


def test_resample_changes_length_for_different_rate():
    audio = np.zeros(1000, dtype=np.float32)
    result = clean_audio.resample(audio, 44100, 48000)
    assert len(result) != len(audio)


def test_highpass_preserves_shape_and_dtype():
    audio = np.random.default_rng(0).standard_normal(2000).astype(np.float32)
    filtered = clean_audio.highpass(audio, 1000)
    assert filtered.shape == audio.shape
    assert filtered.dtype == audio.dtype


def test_lowpass_preserves_shape_and_dtype():
    audio = np.random.default_rng(0).standard_normal(2000).astype(np.float32)
    filtered = clean_audio.lowpass(audio, 1000)
    assert filtered.shape == audio.shape
    assert filtered.dtype == audio.dtype


def test_clean_normalises_and_converts_to_float32():
    audio = np.array([0.0, 2.0, -4.0], dtype=np.float64)
    cleaned = clean_audio.clean(audio)
    assert cleaned.dtype == np.float32
    assert np.max(np.abs(cleaned)) == pytest.approx(1.0, abs=1e-5)


def test_clean_rejects_none_instead_of_silently_substituting_silence():
    # audio_check runs first, so clean(None) must raise rather than
    # returning a silent buffer.
    with pytest.raises(TypeError):
        clean_audio.clean(None)


def test_clean_rejects_empty_array():
    with pytest.raises(ValueError):
        clean_audio.clean(np.array([], dtype=np.float32))


def test_clean_skip_mono_conversion_keeps_stereo_shape():
    stereo = np.ones((10, 2), dtype=np.float32)
    cleaned = clean_audio.clean(stereo, skip_mono_conversion=True)
    assert cleaned.shape == (10, 2)


def test_clean_convert_16bit_returns_int16():
    audio = np.array([0.0, 0.5, -0.5], dtype=np.float32)
    cleaned = clean_audio.clean(audio, convert_16bit=True)
    assert cleaned.dtype == np.int16
