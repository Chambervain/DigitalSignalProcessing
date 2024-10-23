import numpy as np
import pyaudio

# Parameters
SAMPLE_RATE = 44100
DURATION = 2.0
FREQUENCY = 440.0
DECAY_FACTOR = 0.996


# Karplus-Strong Algorithm
def karplus_strong(frequency, sample_rate, duration, decay_factor):
    # Calculate buffer size and initialize with random noise
    buffer_size = int(sample_rate // frequency)
    buffer = np.random.rand(buffer_size) - 0.5

    # Initialize output array
    num_samples = int(sample_rate * duration)
    output = np.zeros(num_samples)

    # Circular buffer index
    index = 0

    for i in range(num_samples):
        output[i] = buffer[index]

        # Update buffer based on the Karplus-Strong update rule
        next_sample = decay_factor * 0.5 * (buffer[index] + buffer[(index + 1) % buffer_size])
        buffer[index] = next_sample
        index = (index + 1) % buffer_size

    return output


# Initialize PyAudio for real-time audio output
p = pyaudio.PyAudio()

# Define stream parameters
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=SAMPLE_RATE,
                output=True)

# Generate and ouput the sound
sound = karplus_strong(FREQUENCY, SAMPLE_RATE, DURATION, DECAY_FACTOR)
stream.write(sound.astype(np.float32).tobytes())

stream.stop_stream()
stream.close()
p.terminate()
