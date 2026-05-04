import json
from pathlib import Path
from .config import config_file, DEFAULT_CONFIG # Source of Truth - I like source of truths, less code!


def load_config():
    if config_file.exists():
        with config_file.open("r") as f:
            return json.load(f)
    return DEFAULT_CONFIG

def save_config(config):
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)


def show_menu():
    print("\nFFT Channel Vocoder Configuration")
    print("=" * 40)
    config = load_config()

    print("\nCurrent Settings:\n")
    print("1. Sample Rate:", config["sample_rate"], "Hz")
    print("2. Vocoder FFT Size (power of 2):", config["vocoder_fft_size"])
    calculated_vocoder_fft = 2 ** config["vocoder_fft_size"]
    print("   Calculated FFT window size:", calculated_vocoder_fft)
    print("3. Vocoder Hop Divisor:", config["vocoder_hop"])
    calculated_hop = calculated_vocoder_fft // config["vocoder_hop"]
    print("   Calculated hop size:", calculated_hop)
    print("4. Pitch Correct FFT Size (power of 2):", config["pitch_correct_fft_size"])
    calculated_pitch_fft = 2 ** config["pitch_correct_fft_size"]
    print("   Calculated pitch FFT size:", calculated_pitch_fft)
    print("5. Pitch Correcter Hop Divisor:", config["pitch_correcter_hop"])
    calculated_pitch_hop = calculated_pitch_fft // config["pitch_correcter_hop"]
    print("   Calculated pitch hop size:", calculated_pitch_hop)
    print("6. Exit and save")

    return config


def edit_setting(config):
    while True:
        config = show_menu()
        choice = input("\nSelect option (1-6): ").strip()

        if choice == "1":
            try:
                value = int(input("Enter sample rate in Hz: ").strip())
                if value > 0:
                    config["sample_rate"] = value
                    save_config(config)
                else:
                    print("Sample rate must be positive.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        elif choice == "2":
            try:
                value = int(
                    input("Enter vocoder FFT size power (e.g., 12 for 4096): ").strip()
                )
                if 4 <= value <= 16:
                    config["vocoder_fft_size"] = value
                    save_config(config)
                else:
                    print("FFT size power should be between 4 and 16.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        elif choice == "3":
            try:
                value = int(input("Enter vocoder hop divisor (1-8): ").strip())
                if 1 <= value <= 8:
                    config["vocoder_hop"] = value
                    save_config(config)
                else:
                    print("Hop divisor should be between 1 and 8.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        elif choice == "4":
            try:
                value = int(
                    input(
                        "Enter pitch correct FFT size power (e.g., 11 for 2048): "
                    ).strip()
                )
                if 4 <= value <= 16:
                    config["pitch_correct_fft_size"] = value
                    save_config(config)
                else:
                    print("FFT size power should be between 4 and 16.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        elif choice == "5":
            try:
                value = int(input("Enter pitch correcter hop divisor (1-8): ").strip())
                if 1 <= value <= 8:
                    config["pitch_correcter_hop"] = value
                    save_config(config)
                else:
                    print("Hop divisor should be between 1 and 8.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        elif choice == "6":
            print("Configuration saved. Exiting.")
            break

        else:
            print("Invalid option. Please select 1-6.")


def configure():
    edit_setting(load_config())

if __name__ == "__main__":
    configure()