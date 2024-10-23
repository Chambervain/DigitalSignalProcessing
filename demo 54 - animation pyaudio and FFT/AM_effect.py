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
CARRIER_FREQ = 3000  # Increase carrier frequency for a "cyber" sound effect

print('Block length: %d' % BLOCKLEN)
print('Duration of block in milliseconds: %.1f' % (1000.0 * BLOCKLEN / RATE))

# Open the audio stream
p = pyaudio.PyAudio()
PA_FORMAT = p.get_format_from_width(WIDTH)

# Input stream (microphone)
input_stream = p.open(
    format=PA_FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=BLOCKLEN
)

# Output stream (speaker/headphones) to play AM-modulated signal
output_stream = p.open(
    format=PA_FORMAT,
    channels=CHANNELS,
    rate=RATE,
    output=True,
    frames_per_buffer=BLOCKLEN
)

# Set up plotting with four plots (2x2 grid)
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

# Output signal plot (after AM modulation)
[g3] = ax3.plot([], [])
ax3.set_xlim(0, 1000 * BLOCKLEN / RATE)
ax3.set_ylim(-10000, 10000)
ax3.set_xlabel('Time (msec)')
ax3.set_title('AM Modulated Output Signal')

# Fourier Transform of output signal
[g4] = ax4.plot([], [])
ax4.set_xlim(0, RATE / 2)
ax4.set_ylim(0, 1000)
ax4.set_xlabel('Frequency (Hz)')
ax4.set_title('Fourier Transform of Output Signal')

my_fig.tight_layout()

# Generate carrier wave (cosine wave) for AM modulation
def generate_carrier_wave(frequency, sample_rate, num_samples):
    t = np.arange(num_samples) / sample_rate
    carrier_wave = np.cos(2 * np.pi * frequency * t)
    return carrier_wave

# Define animation functions
def my_init():
    g1.set_xdata(t)
    g2.set_xdata(f_X)
    g3.set_xdata(t)
    g4.set_xdata(f_X)
    return (g1, g2, g3, g4)

def my_update(i):
    # Read audio input stream
    signal_bytes = input_stream.read(BLOCKLEN, exception_on_overflow=False)
    signal_block = np.frombuffer(signal_bytes, dtype='int16')

    # Generate the carrier wave
    carrier_wave = generate_carrier_wave(CARRIER_FREQ, RATE, BLOCKLEN)

    # Apply AM modulation (multiply input signal with the carrier wave)
    modulated_signal = signal_block * carrier_wave

    # Convert modulated signal to bytes for output
    modulated_bytes = modulated_signal.astype(np.int16).tobytes()

    # Play the AM-modulated signal through output stream
    output_stream.write(modulated_bytes)

    # Compute frequency spectrum for input and modulated output signals
    X_input = np.fft.rfft(signal_block) / BLOCKLEN
    X_modulated = np.fft.rfft(modulated_signal) / BLOCKLEN

    # Update the plots
    g1.set_ydata(signal_block)
    g2.set_ydata(np.abs(X_input))
    g3.set_ydata(modulated_signal)
    g4.set_ydata(np.abs(X_modulated))
    return (g1, g2, g3, g4)

# Read microphone, plot audio signal and AM-modulated output signal
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
input_stream.stop_stream()
input_stream.close()
output_stream.stop_stream()
output_stream.close()
p.terminate()

print('* Finished')
