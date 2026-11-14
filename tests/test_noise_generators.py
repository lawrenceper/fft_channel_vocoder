import numpy as np
import pytest

from fft_channel_vocoder import noise_generators as ng


def test_white_noise_length_and_dtype():
    noise = ng.white_noise(1000)
    assert len(noise) == 1000
    assert noise.dtype == np.float32


def test_pink_noise_length_and_dtype():
    noise = ng.pink_noise(1000)
    assert len(noise) == 1000
    assert noise.dtype == np.float32


def test_brownian_noise_is_normalised():
    noise = ng.brownian_noise(2000)
    assert np.max(np.abs(noise)) <= 1.0 + 1e-6


def test_sine_wave_known_values():
    wave = ng.sine_wave(1.0, 4)
    # At 1 Hz with sample_rate samples per cycle, index 0 should be 0
    assert wave[0] == pytest.approx(0.0, abs=1e-6)


def test_square_wave_only_has_plus_or_minus_one():
    # Includes index 0, where sin() is exactly zero: square_wave() must still
    # report +1.0 there rather than 0.0 (regression test for that edge case).
    wave = ng.square_wave(7.3, 10000)
    assert set(np.unique(wave)) == {-1.0, 1.0}
    assert wave[0] == 1.0


def test_sawtooth_wave_range():
    wave = ng.sawtooth_wave(5.0, 500)
    assert wave.min() >= -1.0 - 1e-6
    assert wave.max() <= 1.0 + 1e-6


def test_triangle_wave_range():
    wave = ng.triangle_wave(5.0, 500)
    assert wave.min() >= -1.0 - 1e-6
    assert wave.max() <= 1.0 + 1e-6


def test_pulse_wave_duty_cycle_fraction_high():
    # Use a sample count that is an exact multiple of the period (48000 / 10
    # Hz = 4800 samples/cycle) so a partial trailing cycle doesn't skew the
    # measured duty cycle.
    wave = ng.pulse_wave(10.0, 4800 * 5, duty_cycle=0.25)
    fraction_high = np.mean(wave > 0)
    assert fraction_high == pytest.approx(0.25, abs=0.005)


def test_impulse_train_spike_count():
    wave = ng.impulse_train(100.0, 4800)  # sample_rate default is 48000
    # period_in_samples = sample_rate // frequency = 480 -> 10 spikes in 4800 samples
    assert np.count_nonzero(wave) == 10


def test_impulse_train_handles_frequency_above_sample_rate():
    # period_in_samples would be 0; must not raise and must return silence
    wave = ng.impulse_train(1_000_000.0, 100)
    assert np.count_nonzero(wave) == 0


def test_tremolo_noise_rejects_invalid_envelope_percentages():
    with pytest.raises(ValueError):
        ng.tremolo_noise(4.0, 1000, attack=-1, hold=50, release=10)


def test_tremolo_noise_rejects_envelope_over_100_percent():
    with pytest.raises(ValueError):
        ng.tremolo_noise(4.0, 1000, attack=60, hold=60, release=10)


def test_tremolo_noise_shape_and_dtype():
    wave = ng.tremolo_noise(4.0, 1000, attack=10, hold=50, release=20)
    assert wave.shape == (1000,)
    assert wave.dtype == np.float32


def test_bandlimited_sawtooth_fft_is_normalised_and_sized():
    wave = ng.bandlimited_sawtooth_fft(220.0, 2048)
    assert len(wave) == 2048
    assert np.max(np.abs(wave)) == pytest.approx(1.0, abs=1e-5)
