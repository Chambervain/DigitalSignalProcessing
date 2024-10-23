# plot_microphone_input_using_animate_play.py

import pyaudio
import matplotlib
from matplotlib import pyplot
from matplotlib import animation
import numpy as np

matplotlib.use('TkAgg')
# matplotlib.use('MacOSX')

print('The matplotlib backend is %s' % pyplot.get_backend())      # Plotting backend


WIDTH = 2           # bytes per sample
CHANNELS = 1        # mono
RATE = 8000         # frames per second

# block length in samples
# BLOCKLEN = 512
BLOCKLEN = 256
# BLOCKLEN = 128

print('Block length: %d' % BLOCKLEN)
print('Duration of block in milliseconds: %.1f' % (1000.0 * BLOCKLEN/RATE))

print('Press q to quit')


# Open the audio stream

p = pyaudio.PyAudio()
PA_FORMAT = p.get_format_from_width(WIDTH)
stream = p.open(
    format = PA_FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input = True,
    output = True,
    frames_per_buffer = BLOCKLEN)   # optional, but can help to reduce latency


# Create figure

my_fig = pyplot.figure(1)
ax1 = my_fig.add_subplot(1, 1, 1)

t = np.arange(BLOCKLEN) * (1000/RATE)   # time axis (milliseconds)

[g1] = ax1.plot([], [])                 # Create empty axis
ax1.set_xlim(0, 1000 * BLOCKLEN/RATE)   # set x-axis limits
ax1.set_ylim(-10000, 10000)             # set y-axis limits
ax1.set_xlabel('Time (msec)')
ax1.set_title('Signal')

# Define animation functions

def my_init():
    g1.set_xdata(t)                   # x-data of plot (discrete-time)
    return (g1,)

def my_update(i):

    # Read audio input stream
    signal_bytes = stream.read(BLOCKLEN, exception_on_overflow = False)

    # Convert binary data to number sequence (numpy array)
    signal_block = np.frombuffer(signal_bytes, dtype = 'int16')

    g1.set_ydata(signal_block)   # Update y-data of plot

    # Convert to binary data, write to audio output stream
    stream.write(signal_block.astype('int16').tobytes(), BLOCKLEN)

    return (g1,)


# Read microphone, plot audio signal

my_anima = animation.FuncAnimation(
    my_fig,
    my_update,
    init_func = my_init,
    interval = 10,   # milliseconds (what happens if this is 200?)
    blit = True,
    cache_frame_data = False,
    repeat = False
)
pyplot.show()   # start animation

stream.stop_stream()
stream.close()
p.terminate()

print('* Finished')