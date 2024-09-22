# filter_16_stereo.py
# Implement a stereo signal with a different frequency in each channel
# Left channel will be a cosine wave with f1, right channel will be a cosine wave with f2
# 16 bit/sample

from math import cos, pi
import pyaudio
import struct

# Fs : Sampling frequency (samples/second)
Fs = 8000

T = 1       # T : Duration of audio to play (seconds)
N = T * Fs  # N : Number of samples to play

# Frequencies for the left and right channels
f1 = 400   # Left channel frequency (Hz)
f2 = 600   # Right channel frequency (Hz)

# Gain to ensure impulse response does not exceed the 16-bit maximum value
gain = 32767

# Create an audio object and open an audio stream for output
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=2,    # Two channels for stereo
                rate=Fs,
                input=False,
                output=True)

# paInt16 is 16 bits/sample
# Run for N samples
for n in range(0, N):

    # Generate signal for left channel (cosine wave at f1 Hz)
    left_channel_value = gain * cos(2 * pi * f1 * n / Fs)

    # Generate signal for right channel (cosine wave at f2 Hz)
    right_channel_value = gain * cos(2 * pi * f2 * n / Fs)

    # Clipping to avoid overflow
    left_channel_value = max(min(left_channel_value, 32767), -32768)
    right_channel_value = max(min(right_channel_value, 32767), -32768)

    # Pack both channels into binary format (left and right)
    data = struct.pack('hh', int(left_channel_value), int(right_channel_value))

    # Write binary data to audio stream
    stream.write(data)

# Close the audio stream
stream.stop_stream()
stream.close()
p.terminate()
