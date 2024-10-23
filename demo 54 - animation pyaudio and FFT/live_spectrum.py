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
CUTOFF_FREQ = 500

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
    output=False,
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

# Output signal plot (after high-pass filter)
[g3] = ax3.plot([], [])
ax3.set_xlim(0, 1000 * BLOCKLEN / RATE)
ax3.set_ylim(-10000, 10000)
ax3.set_xlabel('Time (msec)')
ax3.set_title('Output Signal (Filtered)')

# Fourier Transform of output signal
[g4] = ax4.plot([], [])
ax4.set_xlim(0, RATE / 2)
ax4.set_ylim(0, 1000)
ax4.set_xlabel('Frequency (Hz)')
ax4.set_title('Fourier Transform of Output Signal')
my_fig.tight_layout()

# Define filter coefficients (for a first-order high-pass filter)
def calculate_filter_coefficients(cutoff_freq, sample_rate):
    # Compute the filter coefficient based on the cutoff frequency
    RC = 1.0 / (2 * np.pi * cutoff_freq)
    dt = 1.0 / sample_rate
    alpha = RC / (RC + dt)
    return alpha

# High-pass filter function using the recursive difference equation
def highpass_filter(signal, alpha, previous_input, previous_output):
    # Apply the recursive difference equation for each sample
    output_signal = np.zeros_like(signal)
    for n in range(len(signal)):
        output_signal[n] = alpha * (previous_output + signal[n] - previous_input)
        previous_input = signal[n]
        previous_output = output_signal[n]
    return output_signal, previous_input, previous_output

# Initialize previous input/output for the recursive filter
previous_input = 0
previous_output = 0
alpha = calculate_filter_coefficients(CUTOFF_FREQ, RATE)

# Define animation functions
def my_init():
    g1.set_xdata(t)
    g2.set_xdata(f_X)
    g3.set_xdata(t)
    g4.set_xdata(f_X)
    return (g1, g2, g3, g4)

def my_update(i):
    global previous_input, previous_output
    # Read audio input stream
    signal_bytes = stream.read(BLOCKLEN, exception_on_overflow=False)
    signal_block = np.frombuffer(signal_bytes, dtype='int16')

    # Apply high-pass filter to the input signal
    filtered_signal, previous_input, previous_output = highpass_filter(
        signal_block, alpha, previous_input, previous_output)

    # Compute frequency spectrum for input and output signals
    X_input = np.fft.rfft(signal_block) / BLOCKLEN
    X_output = np.fft.rfft(filtered_signal) / BLOCKLEN

    # Update the plots
    g1.set_ydata(signal_block)
    g2.set_ydata(np.abs(X_input))
    g3.set_ydata(filtered_signal)
    g4.set_ydata(np.abs(X_output))
    return (g1, g2, g3, g4)

# Read microphone, plot audio signal and filtered output signal
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
