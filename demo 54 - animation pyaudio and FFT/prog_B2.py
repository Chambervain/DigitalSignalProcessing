import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import butter, lfilter

# Filter design (high-pass filter)
def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

# Audio and plot parameters
WIDTH = 2
CHANNELS = 1
RATE = 8000  # Sample rate
BLOCKLEN = 512  # Block length in samples
cutoff_freq = 500  # Cutoff frequency for high-pass filter in Hz

# Initialize PyAudio
p = pyaudio.PyAudio()
PA_FORMAT = p.get_format_from_width(WIDTH)

# Attempt to open the stream
try:
    stream = p.open(format=PA_FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=False,
                    frames_per_buffer=BLOCKLEN)
except Exception as e:
    print(f"Error opening stream: {e}")
    p.terminate()

# Setup figure and subplots
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

t = np.arange(BLOCKLEN) * (1000.0 / RATE)  # Time axis in milliseconds
f = np.fft.rfftfreq(BLOCKLEN, d=1.0 / RATE)  # Frequency axis for FFT

# Plot initial empty lines
[line_input, ] = ax1.plot(t, np.zeros(BLOCKLEN))
[line_output, ] = ax3.plot(t, np.zeros(BLOCKLEN))
[line_input_spectrum, ] = ax2.plot(f, np.zeros(BLOCKLEN // 2 + 1))
[line_output_spectrum, ] = ax4.plot(f, np.zeros(BLOCKLEN // 2 + 1))

# Axis limits and labels
ax1.set_xlim(0, max(t))
ax1.set_ylim(-10000, 10000)
ax1.set_xlabel('Time [ms]')
ax1.set_ylabel('Amplitude')
ax1.set_title('Input Signal')

ax2.set_xlim(0, RATE / 2)
ax2.set_ylim(0, 500)
ax2.set_xlabel('Frequency [Hz]')
ax2.set_ylabel('Magnitude')
ax2.set_title('Spectrum of Input Signal')

ax3.set_xlim(0, max(t))
ax3.set_ylim(-10000, 10000)
ax3.set_xlabel('Time [ms]')
ax3.set_ylabel('Amplitude')
ax3.set_title('Output Signal')

ax4.set_xlim(0, RATE / 2)
ax4.set_ylim(0, 500)
ax4.set_xlabel('Frequency [Hz]')
ax4.set_ylabel('Magnitude')
ax4.set_title('Spectrum of Output Signal')

# Function to update plots in animation
def update_plot(frame):
    try:
        # Read audio block
        input_bytes = stream.read(BLOCKLEN, exception_on_overflow=False)
        input_data = np.frombuffer(input_bytes, dtype=np.int16)

        # Apply high-pass filter
        output_data = highpass_filter(input_data, cutoff_freq, RATE)

        # Update time-domain plots
        line_input.set_ydata(input_data)
        line_output.set_ydata(output_data)

        # Compute FFT for both input and output signals
        X_input = np.fft.rfft(input_data)
        X_output = np.fft.rfft(output_data)

        # Update frequency-domain plots
        line_input_spectrum.set_ydata(np.abs(X_input))
        line_output_spectrum.set_ydata(np.abs(X_output))

        return line_input, line_output, line_input_spectrum, line_output_spectrum

    except IOError as e:
        print(f"IOError while reading audio data: {e}")

# Animation function to update the plots
ani = animation.FuncAnimation(fig, update_plot, interval=50, blit=True, cache_frame_data=False)

plt.tight_layout()
plt.show()

# Close stream on exit
if stream.is_active():
    stream.stop_stream()
stream.close()
p.terminate()
