import pyaudio
import struct

# Verify the following results
print(pyaudio.paInt16)

width = 2
print(pyaudio.get_format_from_width(width))

print(pyaudio.paInt8)