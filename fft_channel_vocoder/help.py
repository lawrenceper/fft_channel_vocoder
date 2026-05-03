def show_help():
    help_text = """
FFT Channel Vocoder

USAGE:
vocode                     Run the vocoder with input files
vocode -h or --help        Show this help message
vocode -c or --config      Open configuration menu

INPUT REQUIREMENTS:
The vocoder reads from an input folder. Create a folder named "input" and place your files there.

SUPPORTED INPUT FILES:

Voice Files:
Place one or more voice files as modulators.
File naming: voice1.wav, voice2.wav, etc.

Carrier Wave Options:

1. MIDI Files:
Synthesize melodies as carrier waves.
File naming: melody1.mid, melody2.mid, etc.

2. Synth Wave Files:
Use pre-generated audio files as carriers.
File naming: synth1.wav, synth2.wav, etc.

3. Scale Files for Pitch Correction:
Define musical scales for automatic pitch detection and correction.
File naming: scale1.txt, scale2.txt, etc.
Format: One note per line. Supported notes are c, c#, d, d#, e, f, f#, g, g#, a, a#, b.
Comments start with #. Blank lines are ignored.
Optional parameters: min_freq and max_freq in Hz.
Example scale file:
    # Major scale
    min_freq=50
    max_freq=500
    c
    d
    e
    f
    g
    a
    b

OUTPUT:
The vocoder creates an output folder and saves processed files with combined names.
Example: voice1_melody1.wav, voice1_synth1.wav, voice1_scale1.wav, voice1_whisper.wav

PROCESSING:
For each voice file, the vocoder processes all available carriers:
1. Each MIDI file is synthesized and vocoded
2. Each synth wave file is vocoded
3. Each scale file triggers pitch detection and vocoding
4. A whisper track is generated using white noise

CONFIGURATION:
Run vocode -c to open the configuration menu.
Settings are stored in config.json and include:
- sample_rate: Audio sample rate in Hz
- vocoder_fft_size: FFT window size power (2 to the power of this value)
- vocoder_hop: Hop size divisor for vocoder FFTs
- pitch_correct_fft_size: FFT size power for pitch correction
- pitch_correcter_hop: Hop size divisor for pitch correction FFTs

TROUBLESHOOTING:
If no input files are found, this help message will be shown.
Ensure input folder and files are created before running.
"""
    print(help_text)
