from struct import pack
from math import sin, pi
import wave

Fs = 8000

# Open a new wave file with 3 channels
wf = wave.open('sin_01_tripleChannel.wav', 'w')
wf.setnchannels(3)
wf.setsampwidth(2)
wf.setframerate(Fs)

A = 2 ** 15 - 1.0  # Amplitude

# Set different frequencies for each channel
f1 = 220.0
f2 = 440.0
f3 = 880.0

N = int(0.5 * Fs)

# Loop to generate the signal for each channel
for n in range(0, N):
    # Generate sine wave values for each channel
    x1 = A * sin(2 * pi * f1 / Fs * n)
    x2 = A * sin(2 * pi * f2 / Fs * n)
    x3 = A * sin(2 * pi * f3 / Fs * n)

    # Pack each sample value as a 16-bit integer
    byte_string = pack('hhh', int(x1), int(x2), int(x3))
    wf.writeframes(byte_string)

wf.close()
