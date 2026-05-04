from setuptools import setup, find_packages

setup(
    name="fft_channel_vocoder",
    version="1.0.1Patch1",
    description="FFT-based channel vocoder that applies spectral envelope transfer",
    author="Lawrence Perez",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "scipy",
        "mido",
    ],
    entry_points={
        "console_scripts": [
            "vocode=fft_channel_vocoder.cli:cli",
        ],
    },
)
