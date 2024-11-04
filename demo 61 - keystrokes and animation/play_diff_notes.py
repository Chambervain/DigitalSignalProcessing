import pyaudio
import numpy as np
import tkinter as Tk
from scipy.signal import lfilter
import matplotlib.figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import animation

matplotlib.use('TkAgg')
# Constants
BLOCKLEN = 256
WIDTH = 2
CHANNELS = 1
RATE = 8000
MAXVALUE = 2 ** 15 - 1

# Define frequencies for different notes
f0 = 440.0
frequencies = [f0 * (2 ** (k / 12)) for k in range(26)]
Ta = 0.8
r = 0.005 ** (1.0 / (Ta * RATE))

# Initialize default frequency and filter coefficients
f1 = frequencies[0]
om1 = 2.0 * np.pi * f1 / RATE
a = [1, -2 * r * np.cos(om1), r ** 2]
b = [np.sin(om1)]
states = np.zeros(2)
x = np.zeros(BLOCKLEN)

# Initialize audio stream
p = pyaudio.PyAudio()
PA_FORMAT = pyaudio.paInt16
stream = p.open(
    format=PA_FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=False,
    output=True,
    frames_per_buffer=BLOCKLEN
)

KEYPRESS = False
key_map = {chr(65 + i): frequencies[i] for i in range(26)}


def my_function(event):
    global KEYPRESS, f1, a, b, states
    if event.char.upper() in key_map:
        # Set frequency based on key press and reset filter states
        f1 = key_map[event.char.upper()]
        om1 = 2.0 * np.pi * f1 / RATE
        a = [1, -2 * r * np.cos(om1), r ** 2]
        b = [np.sin(om1)]
        states = np.zeros(2)
        KEYPRESS = True
        print(f"Key pressed: {event.char.upper()}, Frequency set to: {f1} Hz")
    elif event.char == 'q':
        print('Good bye')
        root.quit()


# Define Tkinter root
root = Tk.Tk()
root.bind("<Key>", my_function)
print('Press letter keys (A-Z) for different notes. Press "q" to quit')

# Set up plot
my_fig = matplotlib.figure.Figure()
my_ax = my_fig.add_subplot(1, 1, 1)
[g1] = my_ax.plot([], [])
my_ax.set_ylim(-16000, 16000)
my_ax.set_xlim(0, BLOCKLEN * 1000.0 / RATE)
my_ax.set_xlabel('Time (milliseconds)')
my_ax.set_title('Signal')
my_canvas = FigureCanvasTkAgg(my_fig, master=root)
C1 = my_canvas.get_tk_widget()
C1.pack()
M1 = np.int64(BLOCKLEN / 2)


def my_init():
    t = np.arange(BLOCKLEN) * 1000 / RATE
    g1.set_xdata(t)
    return (g1,)


def my_update(i):
    global states, x, KEYPRESS
    if KEYPRESS:
        x[M1] = 8000.0
        KEYPRESS = False
    y, states = lfilter(b, a, x, zi=states)
    x[M1] = 0.0
    y = np.clip(y, -MAXVALUE, MAXVALUE)
    decay = np.exp(-0.01 * np.arange(BLOCKLEN))
    y = y * decay

    g1.set_ydata(y)
    my_canvas.draw()
    stream.write(y.astype(np.int16).tobytes(), BLOCKLEN)
    return (g1,)


my_anima = animation.FuncAnimation(
    my_fig,
    my_update,
    init_func=my_init,
    interval=20,
    blit=True,
    cache_frame_data=False,
    repeat=False
)

Tk.mainloop()
stream.stop_stream()
stream.close()
p.terminate()

print('* Finished')
