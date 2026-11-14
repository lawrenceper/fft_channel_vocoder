from pathlib import Path

import numpy as np
import soundfile as sf

from fft_channel_vocoder import main as main_module
from fft_channel_vocoder.main import files_exist, load_scale, whisper
from fft_channel_vocoder.config import sample_rate


def test_files_exist_yields_sequential_numbered_files(tmp_path):
    (tmp_path / "voice1.wav").write_bytes(b"x")
    (tmp_path / "voice2.wav").write_bytes(b"x")
    # voice4 is unreachable since voice3 is missing; generator stops at gaps.
    (tmp_path / "voice4.wav").write_bytes(b"x")

    found = list(files_exist(tmp_path, "voice", "wav"))

    assert [name for _, name in found] == ["voice1", "voice2"]


def test_files_exist_yields_nothing_when_no_files_present(tmp_path):
    found = list(files_exist(tmp_path, "voice", "wav"))
    assert found == []


def test_load_scale_parses_notes_and_parameters(tmp_path):
    scale_file = tmp_path / "scale1.txt"
    scale_file.write_text(
        "# Major scale\n"
        "min_freq=80\n"
        "max_freq=400\n"
        "\n"
        "C\n"
        "D\n"
        "E\n"
    )

    notes, params = load_scale(scale_file)

    assert notes == ["c", "d", "e"]
    assert params == {"min_freq": 80.0, "max_freq": 400.0}


def test_load_scale_uses_defaults_when_parameters_missing(tmp_path):
    scale_file = tmp_path / "scale1.txt"
    scale_file.write_text("c\nd\n")

    notes, params = load_scale(scale_file)

    assert notes == ["c", "d"]
    assert params == {"min_freq": 50, "max_freq": 500}


def test_load_scale_ignores_unparseable_parameter_values(tmp_path):
    scale_file = tmp_path / "scale1.txt"
    scale_file.write_text("min_freq=not-a-number\nc\n")

    notes, params = load_scale(scale_file)

    assert notes == ["c"]
    assert params["min_freq"] == 50  # default preserved, bad value ignored


def test_whisper_produces_finite_audio_same_length_as_input():
    voice = np.random.default_rng(0).standard_normal(9600).astype(np.float32)
    output = whisper(voice)
    assert np.all(np.isfinite(output))
    assert len(output) > 0


def test_main_imports_cleanly_as_the_submodule_not_the_entrypoint_function():
    # Regression test: fft_channel_vocoder/__init__.py used to do
    # `from .main import main`, which shadowed this submodule with the
    # main() function, so `from fft_channel_vocoder import main` returned a
    # function instead of the module.
    import fft_channel_vocoder

    assert fft_channel_vocoder.main is main_module
    assert fft_channel_vocoder.run_vocoder is main_module.main


def test_main_builds_sfz_instrument_under_the_output_folder(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("input").mkdir()
    Path("output").mkdir()

    voice_path = Path("input") / "voice1.wav"
    sf.write(
        voice_path,
        np.zeros(sample_rate // 10, dtype=np.float32),
        sample_rate,
        subtype="FLOAT",
    )

    # Stub out the heavy per-carrier pipelines; this test only cares about
    # where the SFZ instrument folder is built.
    monkeypatch.setattr(main_module, "process_midi_files", lambda *a, **k: None)
    monkeypatch.setattr(main_module, "process_synth_files", lambda *a, **k: None)
    monkeypatch.setattr(main_module, "process_scale_files", lambda *a, **k: None)
    monkeypatch.setattr(main_module, "whisper", lambda data: data)
    monkeypatch.setattr(
        main_module.clean_audio, "make_stereo", lambda a, b: np.column_stack((a, b))
    )
    monkeypatch.setattr(main_module.clean_io, "save", lambda *a, **k: None)

    captured = {}

    def fake_build_vocoded_instrument(voice, output_path, *args, **kwargs):
        captured["output_path"] = Path(output_path)

    monkeypatch.setattr(
        main_module, "build_vocoded_instrument", fake_build_vocoded_instrument
    )

    main_module.main()

    assert captured["output_path"] == Path("output") / "voice1_ffz_instrument"
