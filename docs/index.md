# FFT Channel Vocoder Documentation

Welcome to the FFT Channel Vocoder documentation! This guide covers everything from installation to advanced usage for both beginner users and experienced audio engineers.

## Table of Contents

1. **[Installation Guide](01-installation.md)** — System requirements, Python setup, and installation steps
2. **[Quick Start](02-quick-start.md)** — Get your first vocoded audio in 5 minutes
3. **[Understanding the Vocoder](03-understanding.md)** — What the vocoder does and key concepts
4. **[File Organization](04-file-organization.md)** — How to organize your input files
5. **[Configuration Guide](05-configuration.md)** — Customize settings for your workflow
6. **[Advanced Usage](06-advanced-usage.md)** — Batch processing and custom workflows
7. **[Troubleshooting](07-troubleshooting.md)** — Common issues and solutions

## Design and Technical Details

- **[Design Philosophy](../design/index.md)** — Accessibility-first design, why FFT, automation approach
- **[Algorithm Deep Dive](../design/algorithm.md)** — Technical details for audio engineers and researchers

---

## What is the FFT Channel Vocoder?

The FFT Channel Vocoder is a Python tool that applies the spectral characteristics of one audio signal (voice) onto another (a carrier like synthesized melodies or noise). It's commonly used in music production and audio processing to create robotic vocal effects or blend voices with instruments.

## Key Features

- **Spectral Envelope Transfer** — Extracts formant information from voice and applies it to other signals
- **Multiple Input Formats** — Supports voice files, MIDI files, and pre-generated synth waves
- **Batch Processing** — Processes multiple files automatically
- **High-Quality Audio** — Operates at 96 kHz sample rate by default

## Who Should Use This?

- **Audio Engineers** — Create vocoded effects for professional music production
- **Musicians** — Experiment with vocal processing and sound design
- **Researchers** — Study spectral envelope transfer and FFT-based audio processing
- **Beginners** — Learn audio DSP fundamentals through accessible Python code

---

**New to the vocoder?** Start with the [Installation Guide](01-installation.md) or jump straight to [Quick Start](02-quick-start.md).

**Want to understand how it works?** Read [Understanding the Vocoder](03-understanding.md) first.

**Ready to get started?** Check out [File Organization](04-file-organization.md) to prepare your audio files.

**Curious about the design?** See the [Design Philosophy](../design/index.md) to understand why we built it this way and the accessibility principles that guide development.

**Want the technical details?** Check the [Algorithm Deep Dive](../design/algorithm.md) for a complete mathematical and technical explanation.
