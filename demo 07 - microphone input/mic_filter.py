import pyaudio
import wave
import struct
import math

from myfunctions import clip16

# Constants
RATE = 16000
WIDTH = 2
CHANNELS = 1
BLOCKSIZE = 1024
f0 = 400
wf = None

p = pyaudio.PyAudio()

# Open audio stream
stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True)

# Open wave file to write
wf = wave.open('modulated_output.wav', 'w')
wf.setnchannels(CHANNELS)
wf.setsampwidth(WIDTH)
wf.setframerate(RATE)

print("Starting the audio stream...")

# Initialize time variable
theta = 0
TWO_PI = 2 * math.pi
omega = TWO_PI * f0 / RATE

while True:
    # Read audio input stream
    input_bytes = stream.read(BLOCKSIZE, exception_on_overflow=False)

    # Convert binary data to numbers
    input_tuple = struct.unpack('h' * BLOCKSIZE, input_bytes)

    # Create output list for modulated signal
    output_block = [0] * BLOCKSIZE

    # Process each sample for modulation
    for n in range(BLOCKSIZE):
        x_n = input_tuple[n]  # Get current input sample

        # Apply amplitude modulation: y(t) = x(t) * cos(2*pi*f0*t)
        output_block[n] = int(clip16(x_n * math.cos(theta)))

        # Update angle for modulation
        theta += omega
        if theta > TWO_PI:
            theta -= TWO_PI

    # Convert output values to binary data
    output_bytes = struct.pack('h' * BLOCKSIZE, *output_block)

    # Write binary data to audio output stream (to speaker)
    stream.write(output_bytes)

    # Write the same modulated signal to the wave file
    wf.writeframes(output_bytes)

# Close the stream and wave file (never reached in this infinite loop)
stream.stop_stream()
stream.close()
p.terminate()
wf.close()
