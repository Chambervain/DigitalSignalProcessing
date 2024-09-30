import pyaudio
import wave
import struct

from myfunctions import clip16

wavefile = 'author.wav'

print('Play the wave file %s.' % wavefile)

# Open wave file (should be mono channel)
wf = wave.open(wavefile, 'rb')

# Read the wave file properties
num_channels = wf.getnchannels()
RATE = wf.getframerate()
signal_length = wf.getnframes()
width = wf.getsampwidth()

print('The file has %d channel(s).' % num_channels)
print('The frame rate is %d frames/second.' % RATE)
print('The file has %d frames.' % signal_length)
print('There are %d bytes per sample.' % width)

# Fourth-order low-pass filter coefficients
b0 = 0.5
b2 = -0.25
b4 = 0.125
a1 = -0.75
a2 = 0.5
a3 = -0.25
a4 = 0.125

# Canonical form variables: using 4 delay variables (w1, w2, w3, w4)
w1, w2, w3, w4 = 0.0, 0.0, 0.0, 0.0

p = pyaudio.PyAudio()

# Open audio stream
stream = p.open(
    format=pyaudio.paInt16,
    channels=num_channels,
    rate=RATE,
    input=False,
    output=True
)

# Get first frame from wave file
input_bytes = wf.readframes(1)

while len(input_bytes) > 0:

    # Convert binary data to number
    input_tuple = struct.unpack('h', input_bytes)
    input_value = input_tuple[0]

    # Implement the fourth-order difference equation (low-pass filter)
    w0_new = input_value - a1 * w1 - a2 * w2 - a3 * w3 - a4 * w4
    y0 = b0 * w0_new + b2 * w2 + b4 * w4

    # Update delay variables
    w4, w3, w2, w1 = w3, w2, w1, w0_new

    # Convert output value to integer and clip to range
    output_value = int(clip16(y0))

    # Convert output value to binary data
    output_bytes = struct.pack('h', output_value)

    # Write binary data to audio stream
    stream.write(output_bytes)

    # Get next frame from wave file
    input_bytes = wf.readframes(1)

print('* Finished')

stream.stop_stream()
stream.close()
p.terminate()
