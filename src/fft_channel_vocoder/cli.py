import sys
from pathlib import Path
from .help import show_help
from .configure_program import configure
from .main import main as run_vocoder


def cli():
    if len(sys.argv) < 2:
        check_and_run_vocoder()
        return

    arg = sys.argv[1]

    if arg in ["-h", "--help"]:
        show_help()
    elif arg in ["-c", "--config"]:
        configure()
    else:
        check_and_run_vocoder()


def check_and_run_vocoder():
    input_path = Path("input")

    if not input_path.exists():
        print("Error: input folder does not exist.")
        print()
        show_help()
        return

    has_files = False
    for extension in ["wav", "mid", "txt"]:
        if any(input_path.glob(f"*.{extension}")):
            has_files = True
            break

    if not has_files:
        print("Error: No input files found in input folder.")
        print()
        show_help()
        return

    output_path = Path("output")
    output_path.mkdir(exist_ok=True)

    run_vocoder()
