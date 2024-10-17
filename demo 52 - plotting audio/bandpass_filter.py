import pyaudio
import struct
import wave
import matplotlib
from matplotlib import pyplot
from matplotlib import animation

matplotlib.use('TkAgg')
# Specify wave file
wavfile = 'author.wav'
print('Name of wave file: %s' % wavfile)
wf = wave.open(wavfile, 'rb')

# Read wave file properties
RATE = wf.getframerate()
WIDTH = wf.getsampwidth()
LEN = wf.getnframes()
CHANNELS = wf.getnchannels()

print('The file has %d channel(s).'         % CHANNELS)
print('The file has %d frames/second.'      % RATE)
print('The file has %d frames.'             % LEN)
print('The file has %d bytes per sample.'   % WIDTH)

BLOCKLEN = 256
BLOCK_DURATION = 1000.0 * BLOCKLEN / RATE
print('Block length: %d' % BLOCKLEN)
print('Duration of block in milliseconds: %.2f' % BLOCK_DURATION)

# Create block (initialize to zero)
output_block = [0] * BLOCKLEN
input_block = [0] * BLOCKLEN
b0, b1, b2 = 0.1, 0.0, -0.1
a1, a2 = -1.8, 0.81

prev_output1, prev_output2 = 0, 0
p = pyaudio.PyAudio()

PA_FORMAT = p.get_format_from_width(WIDTH)
stream = p.open(
    format=PA_FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=False,
    output=True,
    frames_per_buffer=BLOCKLEN
)

# Set up plotting
fig1 = pyplot.figure(1)
fig1.set_figwidth(8.0)
fig1.set_figheight(6.0)

ax1 = fig1.add_subplot(2, 1, 1)
ax2 = fig1.add_subplot(2, 1, 2)
[g1] = ax1.plot([], [])
[g2] = ax2.plot([], [])

# Define animation functions
def my_init():
    g1.set_xdata([1000 * i / RATE for i in range(BLOCKLEN)])
    g1.set_ydata([0] * BLOCKLEN)
    ax1.set_ylim(-32000, 32000)
    ax1.set_xlim(0, 1000 * BLOCKLEN / RATE)
    ax1.set_xlabel('Time (milliseconds)')
    ax1.set_title('Input Signal')

    g2.set_xdata([1000 * i / RATE for i in range(BLOCKLEN)])
    g2.set_ydata([0] * BLOCKLEN)
    ax2.set_ylim(-32000, 32000)
    ax2.set_xlim(0, 1000 * BLOCKLEN / RATE)
    ax2.set_xlabel('Time (milliseconds)')
    ax2.set_title('Output signal')

    return g1, g2

def my_update(i):
    global prev_output1, prev_output2
    input_bytes = wf.readframes(BLOCKLEN)

    if len(input_bytes) < WIDTH * BLOCKLEN:
        wf.rewind()
        input_bytes = wf.readframes(BLOCKLEN)

    input_block = struct.unpack('h' * BLOCKLEN, input_bytes)

    for n in range(BLOCKLEN):
        output_block[n] = int(b0 * input_block[n] + b1 * input_block[n - 1] + b2 * input_block[n - 2]
                              - a1 * prev_output1 - a2 * prev_output2)
        prev_output2 = prev_output1
        prev_output1 = output_block[n]

    g1.set_ydata(input_block)
    g2.set_ydata(output_block)
    output_bytes = struct.pack('h' * BLOCKLEN, *output_block)
    stream.write(output_bytes, BLOCKLEN)
    return g1, g2

my_anima = animation.FuncAnimation(
    fig1,
    my_update,
    init_func=my_init,
    interval=10,
    blit=True,
    cache_frame_data=False,
    repeat=False
)

fig1.tight_layout()
pyplot.show()
stream.stop_stream()
stream.close()
p.terminate()
wf.close()

print('* Finished')