# play_vibrato_interpolation_ver2.py
# Reads a specified wave file (mono) and plays it with a vibrato effect.
# (Sinusoidally time-varying delay)
# Uses linear interpolation
# 
# Save to wave file (but not suitable for long files or continual real-time processing)

import pyaudio
import wave
import struct
import math
from myfunctions import clip16

# wavfile = 'decay_cosine_mono.wav'
wavfile = 'author.wav'
wavfile = 'cosine_300_hz.wav'

print('Play the wave file: %s.' % wavfile)

# Open wave file
wf = wave.open( wavfile, 'rb')

# Read wave file properties
RATE        = wf.getframerate()     # Frame rate (frames/second)
WIDTH       = wf.getsampwidth()     # Number of bytes per sample
LEN         = wf.getnframes()       # Signal length
CHANNELS    = wf.getnchannels()     # Number of channels

print('The file has %d channel(s).'         % CHANNELS)
print('The file has %d frames/second.'      % RATE)
print('The file has %d frames.'             % LEN)
print('The file has %d bytes per sample.'   % WIDTH)

# Vibrato parameters
f0 = 2          # LFO frequency in Hz
W = 0.015       # W : Sweep width (in units of seconds)
                # W = 0 for no effect
                
Wd = W * RATE   # Wd : W in units of discrete samples (use sampling rate)

freq_ratio = 1 + W * 2 * math.pi * f0
print('The frequency ratio is %.5f \n' % freq_ratio)

# OR
# W = (ratio - 1.0) / (2 * math.pi * f0 )


# Buffer to store past signal values. Initialize to zero.
BUFFER_LEN =  1024          # Set buffer length.
buffer = BUFFER_LEN * [0]   # list of zeros

# Buffer (delay line) indices
i1 = 0
kr = 0  # read index
kw = int(0.5 * BUFFER_LEN)  # write index (initialize to middle of buffer)

print('The buffer is %d samples long.' % BUFFER_LEN)

# Open an output audio stream
p = pyaudio.PyAudio()
stream = p.open(format      = pyaudio.paInt16,
                channels    = 1,
                rate        = RATE,
                input       = False,
                output      = True )

output_all = bytes([])            # complete output signal (byte data)

print ('* Playing...')

# Loop through wave file 
for n in range(0, LEN):

    # Get sample from wave file
    input_bytes = wf.readframes(1)

    # Convert string to number
    (x0,) = struct.unpack('h', input_bytes)

    # Get previous and next buffer values (since kr is fractional)
    kr_prev = int(math.floor(kr))
    frac = kr - kr_prev    # 0 <= frac < 1
    kr_next = kr_prev + 1
    if kr_next == BUFFER_LEN:
        kr_next = 0

    # Compute output value using interpolation
    y0 = (1-frac) * buffer[kr_prev] + frac * buffer[kr_next]

    # Update buffer
    buffer[kw] = x0

    # Increment read index
    i1 = i1 + 1
    if i1 >= BUFFER_LEN:
        # End of buffer. Circle back to front.
        i1 = i1 - BUFFER_LEN

    kr = i1 + Wd * math.sin( 2 * math.pi * f0 * n / RATE )
        # Note: kr is not integer!

    # Ensure that 0 <= kr < BUFFER_LEN
    if kr >= BUFFER_LEN:
        kr = kr - BUFFER_LEN

    # Increment write index    
    kw = kw + 1
    if kw == BUFFER_LEN:
        kw = 0

    # Clip and convert output value to binary data
    output_bytes = struct.pack('h', int(clip16(y0)))

    # Write output to audio stream
    stream.write(output_bytes)

    output_all = output_all + output_bytes     # append new to total

print('* Finished')

stream.stop_stream()
stream.close()
p.terminate()
wf.close()

output_wavefile = wavfile[:-4] + '_vibrato.wav'
print('Writing to wave file', output_wavefile)
wf = wave.open(output_wavefile, 'w')      # wave file
wf.setnchannels(1)      # one channel (mono)
wf.setsampwidth(2)      # two bytes per sample
wf.setframerate(RATE)   # samples per second
wf.writeframes(output_all)
wf.close()
print('* Finished')

