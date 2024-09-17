import wave

# Open the wav file
wf = wave.open('own_voice.wav', 'rb')

# Get basic information about the wav file
num_channels = wf.getnchannels()    # Number of channels
frame_rate = wf.getframerate()      # Frame rate (sampling rate)
num_frames = wf.getnframes()        # Total number of frames
sample_width = wf.getsampwidth()    # Number of bytes per sample

# Print the information
print(f"Number of Channels: {num_channels}")
print(f"Frame Rate (Sampling Rate): {frame_rate} Hz")
print(f"Total Number of Frames: {num_frames}")
print(f"Sample Width: {sample_width} bytes")

wf.close()
