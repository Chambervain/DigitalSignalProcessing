# prog_01_sin.py
# Keyboard control and plotting of a sinusoind using Tkinter.
# Adjust the frequency of the sinusoid by key strokes.

from math import cos, pi 
import matplotlib.figure
from matplotlib import animation

import tkinter as Tk    
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

matplotlib.use('TkAgg')
# matplotlib.use('MacOSX')

print('The matplotlib backend is %s' % matplotlib.get_backend())      # Plotting backend

RATE = 8000           # rate (samples/second)
f1 = 220            # f1 : frequency of sinusoid (Hz)
gain = 0.2 * 2**15
R = 2 ** (1.0/12.0)    # 1.05946309

BLOCKLEN = 512

def my_function(event):
    global f1
    print('You pressed ' + event.char)
    if event.char == 'q':
      print('Good bye')
      root.quit()
    if event.char == 'i':
      f1 = f1 * R       # increase frequency
    if event.char == 'd':
      f1 = f1 / R       # decrease frequency
    print('Frequency = %.2f' % f1)

# Define Tkinter root
root = Tk.Tk()
root.bind("<Key>", my_function)

# Switch to Python window.
print('Press i to increase frequency.')
print('Press d to decrease frequency.')
print('Press q to quit.')

signal_block = [0] * BLOCKLEN
theta = 0

my_fig = matplotlib.figure.Figure()
my_ax = my_fig.add_subplot(1, 1, 1)
[g1] = my_ax.plot([], [])
my_ax.set_ylim(-32000, 32000)
my_ax.set_xlim(0, BLOCKLEN)
my_ax.set_xlabel('Time (index)')
my_ax.set_title('Signal')

# root.focus_set()        # This activates the keyboard (not always needed)

# Turn figure into a Tkinter widget
my_canvas = FigureCanvasTkAgg(my_fig, master = root)
C1 = my_canvas.get_tk_widget()    # canvas widget
C1.pack()                         # place canvas widget


def my_init():
  g1.set_xdata(range(BLOCKLEN))
  return (g1,)

def my_update(i):
  global theta
  global signal_block
  global f1

  om1 = 2.0 * pi * f1 / RATE
  for i in range(0, BLOCKLEN):
    signal_block[i] = gain * cos(theta)
    theta = theta + om1
  while theta > pi:
    theta = theta - 2.0 * pi
  g1.set_ydata(signal_block)
  return (g1,)

my_anima = animation.FuncAnimation(
    my_fig,
    my_update,
    init_func = my_init,
    interval = 20,   # milliseconds (what happens if this is 200?)
    blit = True,
    cache_frame_data = False,
    repeat = False
)

Tk.mainloop()    # Start Tkinter (includes animation)

