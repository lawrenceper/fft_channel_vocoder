import json
from pathlib import Path

config_file = Path(__file__).parent / "config.json"

with open(config_file, "r") as f:
    _config = json.load(f)

sample_rate = _config["sample_rate"]
vocoder_fft_size = _config["vocoder_fft_size"]
vocoder_hop = _config["vocoder_hop"]
pitch_correct_fft_size = _config["pitch_correct_fft_size"]
pitch_correcter_hop = _config["pitch_correcter_hop"]

fft_size = vocoder_fft_size
