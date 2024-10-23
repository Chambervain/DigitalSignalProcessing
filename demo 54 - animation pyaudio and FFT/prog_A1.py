import pyaudio
import struct
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import myfunctions

# Parameters for the filter
a0 = 1
b1 = -0.95  # Example coefficient for a high-pass filter
prev_y = 0  # Previous output sample for recursion

# PyAudio parameters
WIDTH = 2         # bytes per sample
CHANNELS = 1      # mono
RATE = 16000      # Sampling rate (samples/second)
BLOCKLEN = 1024   # Block length in samples

p = pyaudio.PyAudio()

# Open audio stream
stream = p.open(
    format=p.get_format_from_width(WIDTH),
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=BLOCKLEN
)

# For plotting
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

# Initialize input and output plots
x_input = np.zeros(BLOCKLEN)
x_output = np.zeros(BLOCKLEN)
line_input, = ax1.plot(x_input)
line_output, = ax3.plot(x_output)

# Initialize spectrum plots
X_f_input = np.zeros(BLOCKLEN)
X_f_output = np.zeros(BLOCKLEN)
line_f_input, = ax2.plot(X_f_input)
line_f_output, = ax4.plot(X_f_output)

# Plot settings
ax1.set_title('Input signal')
ax3.set_title('Output signal')
ax1.set_ylim(-10000, 10000)
ax3.set_ylim(-10000, 10000)
ax2.set_title('Spectrum of input signal')
ax4.set_title('Spectrum of output signal')

# Function to update the plots
def update_plot(frame):
    global prev_y

    # Read audio input
    input_bytes = stream.read(BLOCKLEN, exception_on_overflow=False)
    input_block = struct.unpack('h' * BLOCKLEN, input_bytes)

    # Apply high-pass filter (difference equation)
    output_block = np.zeros(BLOCKLEN)
    for i in range(BLOCKLEN):
        output_block[i] = a0 * input_block[i] + b1 * prev_y
        prev_y = output_block[i]
        output_block[i] = myfunctions.clip16(output_block[i])

    # Update plots
    line_input.set_ydata(input_block)
    line_output.set_ydata(output_block)

    # FFT for input and output signals
    X_f_input = np.fft.fft(input_block)
    X_f_output = np.fft.fft(output_block)

    # Update frequency plots (only positive frequencies)
    line_f_input.set_ydata(np.abs(X_f_input[:BLOCKLEN // 2]))
    line_f_output.set_ydata(np.abs(X_f_output[:BLOCKLEN // 2]))

    return line_input, line_output, line_f_input, line_f_output

# Animation function, with cache_frame_data=False to suppress the warning
ani = FuncAnimation(fig, update_plot, interval=50, blit=True, cache_frame_data=False)

# Keep the plot running, and stop audio stream only when plot is closed
plt.show()

# Close audio stream after plot is closed
stream.stop_stream()
stream.close()
p.terminate()
