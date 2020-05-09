import functions
from mido import MidiTrack, MetaMessage, Message, MidiFile, bpm2tempo
from time import perf_counter

# Set beat resolution: Pulses (ticks) per quarter note. Normally 480.
PPQN = 480
# Set tempo. Converts bpm to MIDI tempo value (microseconds per quarter note).
tempo = bpm2tempo(60)


# Read input file
print('Reading file...')
t1 = perf_counter()
with open('SPEAR.txt', 'r') as f:
    lines = f.readlines()
t2 = perf_counter()
print('Complete ({:.2f}ms)'.format((t2 - t1) * 1000))


# Parse data
print('Parsing data...')
t1 = perf_counter()
# Get and process partials data. Data lines are 57 characters or longer.
partials = [functions.process_line(line) for line in lines if len(line) >= 57]
t2 = perf_counter()
print('Complete ({:.2f}ms)'.format((t2 - t1) * 1000))


# Convert partials to list of midi-like events (with absolute timings).
# Calculates mean values of pitch and velocity for each event.
print('Constructing MIDI events...')
t1 = perf_counter()
midi_events = []
for partial in partials:
    # Calculate MIDI note number
    average_freq = functions.sublists_index_avg(partial, 1)
    note = functions.freq_to_note(average_freq)
    # Filter out invalid MIDI notes
    if 0 <= note <= 127:
        # Calculate mean velocity
        average_amp = functions.sublists_index_avg(partial, 2)
        velocity = round(functions.linear_scale(average_amp, 0.0, 1.0, 0, 127))
        # Construct and append note on message
        on_time = partial[0][0]
        note_on = ['note_on', on_time, note, velocity]
        midi_events.append(note_on)
        # Construct and append note off message
        off_time = partial[-1][0]
        note_off = ['note_off', off_time, note, velocity]
        midi_events.append(note_off)
t2 = perf_counter()
print('Complete ({:.2f}ms)'.format((t2 - t1) * 1000))


# Sort events by time, convert absolute times to delta times (mutate list).
print('Sorting and processing events...')
t1 = perf_counter()
midi_events.sort(key=lambda x: x[1])
functions.convert_to_delta(midi_events, PPQN, tempo)
t2 = perf_counter()
print('Complete ({:.2f}ms)'.format((t2 - t1) * 1000))


# Set up mido MIDI track.
track0 = MidiTrack()
track0.append(MetaMessage('set_tempo', tempo=tempo))
track0.append(MetaMessage('time_signature', numerator=4, denominator=4))


# Format midi messages and add them to our track
for event in midi_events:
    message, time, note, vel = event
    track0.append(Message(message, time=time, note=note, velocity=velocity))


# Create a MidiFile object, append our track, save the file
midifile = MidiFile()
midifile.tracks.append(track0)
midifile.save('output.mid')
