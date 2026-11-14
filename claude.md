# Coding Details for FFT Vocoder

This is a vocoder written in Python. It is created by visually impaired coder, audio Tinker, and musician and is under the MIT license.

## Project Structure:
### design

Contains markdown files detailing the design of the project.

### docs

Contains documentation for installation and operation of the program.

### fft_channel_vocoder

This folder contains the source code For The entire project:

- __init__.py - required to make this project a Python package
__main__.py, the main entry point for the script, used for the Python package.
- buffers.py, contains a class which generates synthesizer into a buffer Numpy array
- clean_audio.py, contains tools for cleaning audio. Normalization, converting to MONO, converting sampling rate rates so they match, converting to FLOAT32, etc.
- clean_io.py, responsible for loading and saving files while cleaning audio when and if appropriate.
- config.py, main configuration for the script using sensible defaults. Sample rate, FFT size, etc.
- fft.py, the Main FFT vocoder routine.
- main.py, the main automation loop of the script, reads multiple voice files, voice1.wav, voice 2.wav, generates a synth melody based on midi data and runs it through the vocoder, melody1.mid, melody2.mid, takes a synth wave and modulates it with the voice, synth1.wav, synth2.wav, amd finally adds a stereo whisper effect.
- midi_synth.py, takes midi data and synthesizes it.
- noise_generators.py, a bunch of noise generators. Not all of them are used in this project but they might be used eventually or not at all depending on use case.

## Others

Set up and Python project files exists which makes the project pip installable.

## Coding Style

I prefer short, tiny functions with no more than 10 lines each, the exception is for complex conditionals which require more code. I prefer modular code, with one file of code focusing on one specific task. If a module consists of a class, that module should only consist of that class and nothing else. I prefer variable names without abbreviations unless the term is widely used and understood by beginner //intermediate Python coders. Using a variable name like ai_model is OK, but dsp_pipeline should be digital_signal_processing_pipeline.

Sometimes I make code on my own and may need you to correct typos. This is because when reading code only by listening to a screen reader, finding bugs can be tedious with ambiguous trace back messages. Other times, we might build another part of the tool together.

You should explain all code changes in text instead of relying on a visual diff.