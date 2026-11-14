import numpy as np
import pytest

from fft_channel_vocoder.buffers import Carrier_Buffer
from fft_channel_vocoder.config import sample_rate


def test_carrier_buffer_allocates_silence():
    buf = Carrier_Buffer(0.1)
    assert buf.total_samples == int(np.ceil(0.1 * sample_rate))
    assert np.all(buf.carrier == 0.0)
    assert buf.carrier.dtype == np.float32


def test_add_wave_with_positive_frequency_writes_nonzero_samples():
    buf = Carrier_Buffer(0.1)
    buf.add_wave(0.0, 0.05, 220.0)
    written = buf.carrier[: int(0.05 * sample_rate)]
    assert np.any(written != 0.0)


def test_add_wave_with_zero_frequency_uses_white_noise_without_crashing():
    # Regression test: previously raised NameError because white_noise
    # was used without being imported.
    buf = Carrier_Buffer(0.1)
    buf.add_wave(0.0, 0.05, 0.0)
    written = buf.carrier[: int(0.05 * sample_rate)]
    assert np.any(written != 0.0)


def test_add_wave_with_negative_frequency_also_uses_white_noise():
    buf = Carrier_Buffer(0.1)
    buf.add_wave(0.0, 0.05, -10.0)
    written = buf.carrier[: int(0.05 * sample_rate)]
    assert np.any(written != 0.0)


def test_add_wave_raises_if_start_is_past_duration():
    buf = Carrier_Buffer(0.1)
    with pytest.raises(ValueError):
        buf.add_wave(1.0, 1.5, 220.0)


def test_add_wave_clips_end_to_buffer_length():
    buf = Carrier_Buffer(0.05)
    # end_seconds far beyond duration should be capped, not raise or overflow.
    buf.add_wave(0.0, 10.0, 220.0)
    assert len(buf.carrier) == buf.total_samples


def test_add_wave_no_op_when_start_equals_end():
    buf = Carrier_Buffer(0.1)
    buf.add_wave(0.02, 0.02, 220.0)
    assert np.all(buf.carrier == 0.0)


def test_add_fill_writes_across_entire_buffer():
    buf = Carrier_Buffer(0.05)
    buf.add_fill(220.0)
    assert np.any(buf.carrier[: buf.total_samples // 2] != 0.0)
    assert np.any(buf.carrier[buf.total_samples // 2 :] != 0.0)
