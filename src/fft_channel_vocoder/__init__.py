"""FFT Channel Vocoder - Apply spectral envelope transfer using FFT processing."""

# Imported as run_vocoder, not main: binding the name "main" here would
# shadow the main submodule itself (fft_channel_vocoder.main), making the
# submodule unreachable through the package's public attributes.
from .main import main as run_vocoder, files_exist, whisper

__version__ = "0.1.0"
__all__ = ["run_vocoder", "files_exist", "whisper"]
