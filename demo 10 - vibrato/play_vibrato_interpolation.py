import wave
import pyaudio
import struct
import math
from myfunctions import clip16


wavfile = 'author.wav'
wf = wave.open(wavfile, 'rb')

# Read wave file properties
RATE = wf.getframerate()
WIDTH = wf.getsampwidth()
LEN = wf.getnframes()
CHANNELS = wf.getnchannels()

# Vibrato parameters
f0 = 2
W = 0.015
Wd = W * RATE

# Buffer to store past signal values. Initialize to zero.
BUFFER_LEN = 1024
buffer = BUFFER_LEN * [0]

# Buffer (delay line) indices
kr = 0
i1 = kr
kw = int(0.5 * BUFFER_LEN)

# Open an output audio stream
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=False, output=True)

# Function to calculate triangle wave value for the LFO
def triangle_wave(n, rate, freq):
    # Calculate the phase (in radians)
    phase = 2 * math.pi * freq * n / rate
    # Map sine wave to triangle wave using arcsin
    return (2 / math.pi) * math.asin(math.sin(phase))

# Loop through wave file
output_frames = []
for n in range(0, LEN):
    input_bytes = wf.readframes(1)
    x0, = struct.unpack('h', input_bytes)

    # Get previous and next buffer values (since kr is fractional)
    kr_prev = int(math.floor(kr))
    frac = kr - kr_prev    # 0 <= frac < 1
    kr_next = kr_prev + 1
    if kr_next == BUFFER_LEN:
        kr_next = 0

    # Compute output value using interpolation
    y0 = (1 - frac) * buffer[kr_prev] + frac * buffer[kr_next]

    buffer[kw] = x0

    # Increment read index using triangle wave LFO
    i1 = i1 + 1
    if i1 >= BUFFER_LEN:
        i1 = i1 - BUFFER_LEN

    # Use triangle wave instead of sine wave
    kr = i1 + Wd * triangle_wave(n, RATE, f0)

    # Ensure that 0 <= kr < BUFFER_LEN
    if kr >= BUFFER_LEN:
        kr = kr - BUFFER_LEN

    # Increment write index
    kw = kw + 1
    if kw == BUFFER_LEN:
        kw = 0

    output_bytes = struct.pack('h', int(clip16(y0)))

    # Write output to audio stream and save to output frames list
    stream.write(output_bytes)
    output_frames.append(output_bytes)

output_wavfile = 'modified_vibrato_triangle_wave.wav'

wf_output = wave.open(output_wavfile, 'wb')
wf_output.setnchannels(1)
wf_output.setsampwidth(WIDTH)
wf_output.setframerate(RATE)
wf_output.writeframes(b''.join(output_frames))
wf_output.close()

stream.stop_stream()
stream.close()
p.terminate()
wf.close()

print(f"Output saved as {output_wavfile}")
