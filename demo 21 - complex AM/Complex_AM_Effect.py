import pyaudio
import matplotlib
from matplotlib import pyplot
from matplotlib import animation
import numpy as np

matplotlib.use('TkAgg')
print('The matplotlib backend is %s' % pyplot.get_backend())

WIDTH = 2
CHANNELS = 1
RATE = 8000
BLOCKLEN = 512
MOD_FREQ = 1000

print('Block length: %d' % BLOCKLEN)
print('Duration of block in milliseconds: %.1f' % (1000.0 * BLOCKLEN / RATE))

# Open the audio stream
p = pyaudio.PyAudio()
PA_FORMAT = p.get_format_from_width(WIDTH)
stream = p.open(
    format=PA_FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=BLOCKLEN
)

# Set up plotting with four plots
my_fig, ((ax1, ax2), (ax3, ax4)) = pyplot.subplots(2, 2)
t = np.arange(BLOCKLEN) * (1000 / RATE)
x = np.zeros(BLOCKLEN)
X = np.fft.rfft(x)
f_X = np.arange(X.size) * RATE / BLOCKLEN

# Input signal plot
[g1] = ax1.plot([], [])
ax1.set_xlim(0, 1000 * BLOCKLEN / RATE)
ax1.set_ylim(-10000, 10000)
ax1.set_xlabel('Time (msec)')
ax1.set_title('Input Signal')

# Fourier Transform of input signal
[g2] = ax2.plot([], [])
ax2.set_xlim(0, RATE / 2)
ax2.set_ylim(0, 1000)
ax2.set_xlabel('Frequency (Hz)')
ax2.set_title('Fourier Transform of Input Signal')

# Output signal plot (after complex AM effect)
[g3] = ax3.plot([], [])
ax3.set_xlim(0, 1000 * BLOCKLEN / RATE)
ax3.set_ylim(-10000, 10000)
ax3.set_xlabel('Time (msec)')
ax3.set_title('Output Signal (AM Effect)')

# Fourier Transform of output signal
[g4] = ax4.plot([], [])
ax4.set_xlim(0, RATE / 2)
ax4.set_ylim(0, 1000)
ax4.set_xlabel('Frequency (Hz)')
ax4.set_title('Fourier Transform of Output Signal')
my_fig.tight_layout()


# Function to apply the complex AM effect
def complex_am_effect(signal, mod_freq, sample_rate):
    t = np.arange(len(signal)) / sample_rate
    modulator = np.sin(2 * np.pi * mod_freq * t)
    return signal * modulator


# Define animation functions
def my_init():
    g1.set_xdata(t)
    g2.set_xdata(f_X)
    g3.set_xdata(t)
    g4.set_xdata(f_X)
    return (g1, g2, g3, g4)


def my_update(i):
    # Read audio input stream
    signal_bytes = stream.read(BLOCKLEN, exception_on_overflow=False)
    signal_block = np.frombuffer(signal_bytes, dtype='int16')

    # Apply complex AM effect to the input signal
    am_signal = complex_am_effect(signal_block, MOD_FREQ, RATE)
    # Compute frequency spectrum for input and output signals
    X_input = np.fft.rfft(signal_block) / BLOCKLEN
    X_output = np.fft.rfft(am_signal) / BLOCKLEN

    # Update the plots
    g1.set_ydata(signal_block)
    g2.set_ydata(np.abs(X_input))
    g3.set_ydata(am_signal)
    g4.set_ydata(np.abs(X_output))

    # Play the processed (AM) signal through the output
    stream.write(am_signal.astype(np.int16).tobytes())

    return (g1, g2, g3, g4)


my_anima = animation.FuncAnimation(
    my_fig,
    my_update,
    init_func=my_init,
    interval=10,
    blit=True,
    cache_frame_data=False,
    repeat=False
)

pyplot.show()
stream.stop_stream()
stream.close()
p.terminate()

print('* Finished')
