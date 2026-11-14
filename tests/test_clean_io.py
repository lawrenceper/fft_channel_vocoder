import numpy as np
import soundfile as sf

from fft_channel_vocoder import clean_io
from fft_channel_vocoder.config import sample_rate


def test_does_exist_true_for_existing_file(tmp_path):
    file_path = tmp_path / "present.wav"
    file_path.write_bytes(b"not really a wav, just needs to exist")
    assert clean_io.does_exist(file_path) is True


def test_does_exist_false_for_missing_file(tmp_path):
    assert clean_io.does_exist(tmp_path / "missing.wav") is False


def test_does_exist_false_for_directory(tmp_path):
    # Opening a directory with open(..., "r") raises IsADirectoryError, which
    # is an OSError subclass and should be treated as "does not exist".
    assert clean_io.does_exist(tmp_path) is False


def test_save_and_load_roundtrip_mono(tmp_path):
    original = np.linspace(-0.5, 0.5, sample_rate // 10, dtype=np.float32)
    file_path = tmp_path / "voice.wav"

    clean_io.save(file_path, original)
    loaded = clean_io.load(file_path)

    assert loaded.dtype == np.float32
    assert len(loaded) == len(original)


def test_save_stereo_writes_two_channels(tmp_path):
    left = np.linspace(-0.5, 0.5, 1000, dtype=np.float32)
    right = np.linspace(0.5, -0.5, 1000, dtype=np.float32)
    stereo = np.column_stack((left, right))
    file_path = tmp_path / "stereo.wav"

    clean_io.save(file_path, stereo)

    audio, _ = sf.read(file_path)
    assert audio.shape[1] == 2


def test_load_resamples_mismatched_sample_rate(tmp_path):
    other_rate = sample_rate // 2
    audio = np.linspace(-0.5, 0.5, other_rate // 2, dtype=np.float32)
    file_path = tmp_path / "other_rate.wav"
    sf.write(file_path, audio, other_rate, subtype="FLOAT")

    loaded = clean_io.load(file_path)

    # Resampled length should scale roughly with the sample rate ratio.
    expected_length = len(audio) * sample_rate / other_rate
    assert abs(len(loaded) - expected_length) < sample_rate * 0.01
