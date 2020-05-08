from doctest import testmod
from mido import second2tick
from math import log


def convert_to_delta(midi_events):
    """ (list of list of [str, float, int, int]) -> None

    Mutates midi_events, replacing absolute time values (in seconds) with delta
    time values between events (in ticks)
    midi_events is pre-sorted by absolute time (index [1] of each inner list).

    >>> convert_to_delta([['note_on', 0.0, 64, 64], ['note_off', 0.1, 64, 64],
    ...                   ['note_on', 0.1, 65, 64], ['note_off', 0.5, 65, 64]])

    """

    # Working backwards from the end of the list up to [1] inclusive, find the
    # difference between each item and the item with the next-smallest index.
    # Convert this value to ticks and Overwrite the item with the result.
    # Process [0] seperately at the end.
    for i in reversed(range(1, len(midi_events))):
        delta_seconds = midi_events[i][1] - midi_events[i - 1][1]
        # Tick conversion assumes beats-per-tick of 480 and
        # tempo of 1000000 (60bpm)
        delta_ticks = round(second2tick(delta_seconds, 480, 1000000))
        midi_events[i][1] = delta_ticks
    midi_events[0][1] = round(second2tick(midi_events[0][1], 480, 1000000))


def freq_to_note(frequency):
    """ (number) -> int

    Returns the nearest MIDI note number to frequency (in Hz).
    Assumes that MIDI note 69 (A4) is 440Hz.

    >>> freq_to_note(880.1)
    81
    """

    midi_note = round(12 * log(frequency / 440, 2) + 69)

    return midi_note


def linear_scale(input, in_low, in_high, out_low, out_high):
    """ (number, number, number, number, number) -> float

    Linear scaling. Scales old_value in the range (in_high - in-low) to a value
    in the range (out_high - out_low). Returns the result.

    >>> linear_scale(0.5, 0.0, 1.0, 0, 127)
    63.5

    """

    in_range = (in_high - in_low)
    out_range = (out_high - out_low)
    result = (((input - in_low) * out_range) / in_range) + out_low

    return result


def process_line(line):
    """ (list of str) -> list of list of float

    Parses line, a line of time, frequency and amplitude data output by
    SPEAR in the 'text - partials' format.
    Returns a list of timepoints. Each timepoint is a list of floats
    in the form: [<time in s>, <frequency in Hz>, <amplitude 0.0-1.0>]

    >>> process_line('0.145 443.309723 0.112565 0.1575 443.597656 0.124895')
    [[0.145, 443.309723, 0.112565], [0.1575, 443.597656, 0.124895]]

    """
    partial = []

    split_line = line.strip().split()
    while len(split_line) > 0:
        timepoint = []
        for i in range(3):
            item = float(split_line.pop(0))
            timepoint.append(item)
        partial.append(timepoint)

    return partial


def sublists_index_avg(list, index):
    """ (list of list of number) -> float

    Returns the mean of all values of a specified index in sublists of list.

    >>> sublists_index_avg([[1, 2, 3], [2, 3, 4]], 2)
    3.5
    """

    sum = 0
    for item in list:
        sum += item[index]
    mean = sum / len(list)
    return mean


if __name__ == '__main__':
    testmod()
