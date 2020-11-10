import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
import time
import pretty_midi
import pprint

sample_rate = 44100

def window(x):
    t = np.linspace(-len(x)//2, len(x)//2 - 1, len(x))
    y = np.sinc(2 * t/len(t)) ## lanczos window
    # y = 0.62 - 0.48 * abs(t/len(t) - 1/2) - 0.38 * np.cos(2 * np.pi * t / len(t)) ## bartlett-hann
    return x * y

def sine(freq, phase, amplitude, start, duration):
    global sample_rate
    timeline = np.linspace(start, start+duration, int(duration * sample_rate))
    x = amplitude * np.sin(2 * freq * np.pi * timeline + phase)
    last_phase = 2 * freq * np.pi * timeline[-1]
    # print(last_phase, np.sin(last_phase))
    # plt.plot(timeline, x)
    # plt.show()
    return x, last_phase

## 1

def ex1():
    global sample_rate, sd
    c_maj = [261.53, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]

    time_frame = 3
    note_duration = time_frame/len(c_maj)
    samples = np.zeros(shape=(int(time_frame * sample_rate),), dtype=np.float64)
    phase = 0
    for index, f in enumerate(c_maj):
        x, phase = sine(f, phase, 1e4, 0, note_duration)
        start_time = int(index * note_duration * sample_rate)
        samples[start_time:start_time+len(x) - 1] = samples[start_time:start_time+len(x) - 1] + window(x[:-1])

    sd.default.samplerate = sample_rate
    wav_wave = np.array(samples, dtype=np.int16)
    sd.play(wav_wave, blocking=True)
    sd.stop()

    ## arperggio
    c_arp = [261.53, 329.63, 392.00, 523.25]
    time_frame = 1
    note_duration = time_frame/len(c_arp)
    samples = np.zeros(shape=(int(time_frame * sample_rate),), dtype=np.float64)
    phase = 0
    for index, f in enumerate(c_arp):
        x, phase = sine(f, phase, 1e4, 0, note_duration)
        start_time = int(index * note_duration * sample_rate)
        samples[start_time:start_time+len(x)] = samples[start_time:start_time+len(x)] + window(x)

    sd.default.samplerate = sample_rate
    wav_wave = np.array(samples, dtype=np.int16)
    sd.play(wav_wave, blocking=True)
    sd.stop()

    ## c maj 7 chord
    c_chord = [261.53, 329.63, 392.00, 493.88, 523.25]
    time_frame = 2
    note_duration = time_frame
    samples = np.empty(shape=(len(c_chord),), dtype=np.ndarray)
    for index, f in enumerate(c_chord):
        x, _ = sine(f, 0, 5e3, 0, note_duration)
        samples[index] = window(x)

    samples = samples.sum(axis=0)

    sd.default.samplerate = sample_rate
    wav_wave = np.array(samples, dtype=np.int16)
    sd.play(wav_wave, blocking=True)
    sd.stop()

# ex1()

## 2

def ex2():
    c_maj = [261.53, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
    frere_jaq = [
        (c_maj[0], 2),
        (c_maj[1], 2),
        (c_maj[2], 2),
        (c_maj[0], 2),
        (c_maj[0], 2),
        (c_maj[1], 2),
        (c_maj[2], 2),
        (c_maj[0], 2),
        (c_maj[2], 2),
        (c_maj[3], 2),
        (c_maj[4], 2),
        (0, 2),
        (c_maj[2], 2),
        (c_maj[3], 2),
        (c_maj[4], 2),
        (0, 2),
        (c_maj[4], 1),
        (c_maj[5], 1),
        (c_maj[4], 1),
        (c_maj[3], 1),
        (c_maj[2], 2),
        (c_maj[0], 2),
        (c_maj[4], 1),
        (c_maj[5], 1),
        (c_maj[4], 1),
        (c_maj[3], 1),
        (c_maj[2], 2),
        (c_maj[0], 2),
        (c_maj[1], 2),
        (c_maj[4], 2),
        (c_maj[0], 2),
        (0, 2),
        (c_maj[1], 2),
        (c_maj[4], 2),
        (c_maj[0], 2),
        (0, 2)
    ]

    time_interval_sum = sum (i[1] for i in frere_jaq)

    time_frame = 16
    note_duration = time_frame/time_interval_sum
    samples = np.array([])
    phase = 0
    for f in frere_jaq:
        if f[0] != 0:
            x, phase = sine(f[0], phase, 1e4, 0, note_duration * f[1])
            samples = np.append(samples, window(x), axis=0)
        else:
            x = np.linspace(0, note_duration * f[1], int(note_duration * f[1] * sample_rate))
            samples = np.append(samples, window(x), axis=0)
            phase = 0

    sd.default.samplerate = sample_rate
    wav_wave = np.array(samples, dtype=np.int16)
    sd.play(wav_wave, blocking=True)
    sd.stop()

# ex2()

## 3



def ex3():
    global sample_rate, sd
    midi_data = pretty_midi.PrettyMIDI("01-Recorded MIDI MIDI 001.mid") ## black sabbath - i
    # midi_data = pretty_midi.PrettyMIDI("16752.mid") ## beethoven moonlight sonata - kinda long
    midi_list = []

    ## parsare luata din primul exemplu de aici
    ## https://www.audiolabs-erlangen.de/resources/MIR/FMP/C1/C1S2_MIDI.html
    for instrument in midi_data.instruments:
        for note in instrument.notes:
            start = note.start
            end = note.end
            pitch = note.pitch
            velocity = note.velocity
            midi_list.append([start, end-start, pitch, velocity])
            
    time_frame = midi_data.get_end_time() ## in seconds
    samples = np.empty(shape=(int(time_frame * sample_rate),), dtype=np.float64)
    
    for tone in midi_list:
        x, _ = sine(pretty_midi.note_number_to_hz(tone[2]), 0, 5e3 * (tone[3] / 127), tone[0], tone[1])
        start_time = int(tone[0] * sample_rate)
        samples[start_time:(start_time+len(x))] = samples[start_time:(start_time+len(x))] + window(x)

    sd.default.samplerate = sample_rate
    wav_wave = np.array(samples, dtype=np.int16)
    sd.play(wav_wave, blocking=True)
    sd.stop()


ex3()