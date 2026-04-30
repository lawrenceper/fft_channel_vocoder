# Installation Guide

This guide will help you install the FFT Channel Vocoder on your system. Follow the steps for your operating system.

## System Requirements

- **Python 3.8 or higher** (check with `python3 --version`)
- **macOS**, **Windows**, or **Linux**
- **150 MB** disk space
- **2 GB RAM** (recommended for processing audio files)

## Prerequisites

### 1. Install Python (if you don't have it)

#### macOS
```bash
# Using Homebrew (recommended)
brew install python3

# Or download from python.org
# https://www.python.org/downloads/
```

#### Windows
1. Download Python from https://www.python.org/downloads/
2. Run the installer
3. ✅ **IMPORTANT**: Check "Add Python to PATH"
4. Click Install Now

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip

# Arch
sudo pacman -S python python-pip
```

### 2. Verify Installation

Open a terminal (Command Prompt on Windows) and run:
```bash
python3 --version
pip3 --version
```

You should see version numbers like `Python 3.9.0` and `pip 21.0.1`.

## Installation Steps

### Option A: Install from Source (Recommended for Development)

1. **Download or clone the repository**
   ```bash
   cd ~/Documents
   git clone https://github.com/your-username/fft_channel_vocoder.git
   cd fft_channel_vocoder
   ```
   
   Or download the ZIP file and extract it.

2. **Install in development mode**
   ```bash
   pip3 install -e .
   ```

### Option B: Install from PyPI (Once Released)

```bash
pip3 install fft_channel_vocoder
```

## Verify Installation

Test that the vocoder is installed correctly:

```bash
vocode --help
```

Or run it as a Python module:
```bash
python3 -m fft_channel_vocoder
```

You should see the program running without errors.

## Troubleshooting Installation

### "command not found: vocode"

**Problem**: The `vocode` command isn't recognized.

**Solutions**:
- Make sure you're in a terminal/command prompt (not just Python shell)
- Try `python3 -m fft_channel_vocoder` instead
- On Windows, restart your terminal after installation
- Try installing again: `pip3 install -e .`

### "No module named 'numpy'"

**Problem**: Missing dependencies.

**Solution**:
```bash
pip3 install numpy scipy mido
```

### Permission denied (macOS/Linux)

**Problem**: You get a permission error during installation.

**Solution**: Use the `--user` flag:
```bash
pip3 install -e . --user
```

### Python 2 vs Python 3

**Problem**: You have Python 2 installed and it runs instead of Python 3.

**Solution**: Always use `python3` and `pip3` explicitly (not `python` or `pip`).

## Next Steps

✅ Installation complete! Now:
- Read the [Quick Start Guide](02-quick-start.md) to process your first audio
- Check [File Organization](04-file-organization.md) to prepare your audio files
- See [Understanding the Vocoder](03-understanding.md) to learn the concepts

---

**Still having issues?** Check the [Troubleshooting](07-troubleshooting.md) section or ensure you have the correct Python and pip versions.
