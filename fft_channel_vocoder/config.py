import json
from pathlib import Path

config_file = Path(__file__).parent / "config.json"

DEFAULT_CONFIG = {
    "sample_rate": 96000,
    "vocoder_fft_size": 12,
    "vocoder_hop": 4,
    "pitch_correct_fft_size": 12,
    "pitch_correcter_hop": 4,
}


def _load_or_create_config():
    if not config_file.exists():
        with open(config_file, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        return DEFAULT_CONFIG

    with open(config_file, "r") as f:
        return json.load(f)


_config = _load_or_create_config()

sample_rate = _config["sample_rate"]
vocoder_fft_size = _config["vocoder_fft_size"]
vocoder_hop = _config["vocoder_hop"]
pitch_correct_fft_size = _config["pitch_correct_fft_size"]
pitch_correcter_hop = _config["pitch_correcter_hop"]

fft_size = vocoder_fft_size
