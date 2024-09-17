# write_sin_08
#
# Make a wave file (.wav) consisting of a sine wave

# 8 bits per sample

from struct import pack
from math import sin, pi
import wave

Fs = 8000

# Write a mono wave file
wf = wave.open('sin_08_mono.wav', 'w')  # wf : wave file
wf.setnchannels(1)  # one channel (mono)
wf.setsampwidth(1)  # one byte per sample (8 bits per sample)
wf.setframerate(Fs)  # samples per second
A = 127.0  # amplitude (max value for 8-bit audio is 127)
f = 220.0  # frequency in Hz (note A3)
N = int(0.5 * Fs)  # half-second in samples

for n in range(0, N):  # half-second loop
    x = A * sin(2 * pi * f / Fs * n)
    byte_string = pack('B', int(x + 128))  # 'B' stands for 'unsigned char' (8 bits), with 128 offset for unsigned
    wf.writeframesraw(byte_string)

wf.close()
