# sfz.py

# Writes simple SFZ instrument files mapping MIDI notes to sample files.


def write_sfz(output_path, note_sample_pairs):
    """Write an SFZ instrument file mapping MIDI notes to sample files.

    Args:
        output_path: Path to the .sfz file to create.
        note_sample_pairs: Iterable of (midi_note, sample_filename) tuples.
    """
    with open(output_path, "w") as file:
        for midi_note, sample_filename in note_sample_pairs:
            file.write(f"<region> sample={sample_filename} key={midi_note} loop_mode=one_shot\n")
