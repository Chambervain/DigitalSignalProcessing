import pyaudio
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
import wave

# Parameters
SAMPLE_RATE = 44100
DURATION = 2.0
INITIAL_FREQUENCY = 440.0
INITIAL_GAIN = 1.0
RECORD_TIME = 5
SMOOTHING_STEPS = 500


class SineWaveGenerator:
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.frequency = INITIAL_FREQUENCY
        self.phase = 0
        self.current_gain = INITIAL_GAIN
        self.target_gain = INITIAL_GAIN
        self.smoothing_step = 0
        self.smoothing_gain = np.linspace(self.current_gain, self.target_gain, SMOOTHING_STEPS)
        self.update_phase_increment()

    def update_phase_increment(self):
        self.phase_increment = 2 * np.pi * self.frequency / self.sample_rate

    def generate_samples(self, num_samples):
        # Generate sine wave samples with the updated frequency
        t = np.arange(num_samples) * self.phase_increment + self.phase
        self.phase = (self.phase + num_samples * self.phase_increment) % (2 * np.pi)

        # Apply gain smoothing
        if self.smoothing_step < SMOOTHING_STEPS:
            steps_left = SMOOTHING_STEPS - self.smoothing_step
            if num_samples <= steps_left:
                gain = np.linspace(self.current_gain, self.target_gain, steps_left)[:num_samples]
                self.smoothing_step += num_samples
            else:
                gain = np.concatenate([
                    np.linspace(self.current_gain, self.target_gain, steps_left),
                    np.full(num_samples - steps_left, self.target_gain)
                ])
                self.smoothing_step = SMOOTHING_STEPS
                self.current_gain = self.target_gain
        else:
            gain = np.full(num_samples, self.target_gain)

        # Apply gain to the sine wave
        samples = gain * np.sin(t)
        return samples.astype(np.float32)


# GUI for gain and frequency sliders
class App:
    def __init__(self, root, generator):
        self.generator = generator
        self.stream = self.setup_audio_stream()

        # Create sliders for gain and frequency control
        self.gain_slider = tk.Scale(root, from_=0, to_=2, resolution=0.01, orient='horizontal', label='Gain')
        self.gain_slider.set(INITIAL_GAIN)
        self.gain_slider.pack(side=tk.LEFT, padx=10)
        self.gain_slider.bind("<Motion>", self.update_gain)

        self.frequency_slider = tk.Scale(root, from_=20, to_=2000, resolution=1, orient='horizontal', label='Frequency')
        self.frequency_slider.set(INITIAL_FREQUENCY)
        self.frequency_slider.pack(side=tk.RIGHT, padx=10)
        self.frequency_slider.bind("<Motion>", self.update_frequency)
        self.audio_frames = []
        self.play_audio()

    def setup_audio_stream(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=SAMPLE_RATE,
                        output=True,
                        stream_callback=self.callback)
        return stream

    def callback(self, in_data, frame_count, time_info, status):
        # Generate and play sine wave
        samples = self.generator.generate_samples(frame_count)
        self.audio_frames.append(samples.copy())
        return (samples.tobytes(), pyaudio.paContinue)

    def update_gain(self, event):
        self.generator.target_gain = self.gain_slider.get()
        self.generator.smoothing_step = 0

    def update_frequency(self, event):
        self.generator.frequency = self.frequency_slider.get()
        self.generator.update_phase_increment()

    def play_audio(self):
        self.stream.start_stream()

    def stop_audio(self):
        self.stream.stop_stream()
        self.stream.close()

    def plot_waveform(self):
        # Convert stored frames to a single array
        all_samples = np.concatenate(self.audio_frames)
        # Plot the waveform
        plt.plot(all_samples[:SAMPLE_RATE * RECORD_TIME])
        plt.title("Waveform after Gain Smoothing")
        plt.xlabel("Samples")
        plt.ylabel("Amplitude")
        plt.show()

    def save_waveform(self, filename="output.wav"):
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(4)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join([frame.tobytes() for frame in self.audio_frames]))
        wf.close()


# Main application
if __name__ == "__main__":
    root = tk.Tk()
    generator = SineWaveGenerator()
    app = App(root, generator)
    root.mainloop()
    app.plot_waveform()
    app.save_waveform()
