import pytest

from fft_channel_vocoder.pitch_corrector import (
    circular_distance,
    frequency_to_midi_note,
    frequency_to_note_class,
    midi_note_to_frequency,
    snap_note_to_scale,
)


def test_midi_note_to_frequency_a4_is_440():
    assert midi_note_to_frequency(69) == pytest.approx(440.0)


def test_frequency_to_midi_note_is_inverse_of_midi_note_to_frequency():
    for note in [40, 60, 69, 90]:
        freq = midi_note_to_frequency(note)
        assert frequency_to_midi_note(freq) == pytest.approx(note, abs=1e-6)


def test_frequency_to_note_class_identifies_a():
    assert frequency_to_note_class(440.0) == "a"


def test_frequency_to_note_class_identifies_c():
    # C4 = MIDI note 60
    assert frequency_to_note_class(midi_note_to_frequency(60)) == "c"


def test_circular_distance_adjacent_notes():
    assert circular_distance(0, 1) == 1


def test_circular_distance_wraps_around_the_octave():
    # c (0) and b (11) are one semitone apart going the other way around
    assert circular_distance(0, 11) == 1


def test_circular_distance_is_symmetric():
    assert circular_distance(2, 9) == circular_distance(9, 2)


def test_snap_note_to_scale_returns_none_for_unknown_note_class():
    assert snap_note_to_scale("h", ["c", "d"]) is None


def test_snap_note_to_scale_returns_none_when_scale_is_empty():
    assert snap_note_to_scale("c", []) is None


def test_snap_note_to_scale_picks_exact_match():
    assert snap_note_to_scale("d", ["c", "d", "e"]) == "d"


def test_snap_note_to_scale_ignores_invalid_entries_without_misaligning_index():
    # Regression test: an invalid note earlier in the list used to shift the
    # index lookup and could return the invalid note itself.
    assert snap_note_to_scale("d", ["not-a-note", "d"]) == "d"


def test_snap_note_to_scale_uses_circular_distance_near_octave_boundary():
    # "c" (0) is 1 semitone from "b" (11) going around the circle, and should
    # win over "d" (2) which is farther away on a true circular scale.
    assert snap_note_to_scale("c", ["b", "d"]) == "b"
