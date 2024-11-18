import tkinter as tk
from tkinter import ttk
import numpy as np
import pyaudio
import wave
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.fft import fft


class ShepardRissetApp:
    def __init__(self, master):
        self.master = master
        master.title("Shepard-Risset Glissando")
        # Define initial parameters
        self.base_frequency = tk.DoubleVar(value=200.0)
        self.num_octaves = 3
        self.tones_per_octave = 4
        self.glissando_rate = tk.DoubleVar(value=0.02)
        self.direction = tk.StringVar(value="Ascending")
        self.volume = tk.DoubleVar(value=1.0)
        self.num_tones = 12
        # PyAudio parameters
        self.sample_rate = 44100
        self.frames_per_buffer = 512
        # Initialize time variable and audio phases
        self.global_time = 0.0
        self.phases = np.zeros(self.num_tones)
        self.initial_positions = np.linspace(0, 1, self.num_tones, endpoint=False)
        self.is_recording = True
        self.audio_frames = []
        self.current_buffer = np.zeros(self.frames_per_buffer)
        # Set up plotting
        self.setup_plot()
        self.create_widgets()
        # Set up audio
        self.setup_audio()
        self.is_running = True
        self.master.after(0, self.audio_loop)
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=30, blit=True, cache_frame_data=False)

    def create_widgets(self):
        ttk.Label(self.master, text="").pack()
        ttk.Label(self.master, text="").pack()
        ttk.Label(self.master, text="").pack()
        ttk.Label(self.master, text="").pack()

        # Frequency slider
        ttk.Label(self.master, text="Shepard Tone Frequency (Hz)").pack()
        self.base_freq_slider = ttk.Scale(
            self.master, from_=50, to=450, variable=self.base_frequency, orient=tk.HORIZONTAL)
        self.base_freq_slider.pack(fill=tk.X, padx=int(self.master.winfo_screenwidth() * 0.2))

        # Volume slider
        ttk.Label(self.master, text="Sound Volume").pack()
        self.volume_slider = ttk.Scale(
            self.master, from_=0.0, to=1.0, variable=self.volume, orient=tk.HORIZONTAL)
        self.volume_slider.pack(fill=tk.X, padx=int(self.master.winfo_screenwidth() * 0.2))

        # Rate of Change slider
        ttk.Label(self.master, text="Glissando Rate of Change").pack()
        self.glissando_rate_slider = ttk.Scale(
            self.master, from_=0.01, to=0.1, variable=self.glissando_rate, orient=tk.HORIZONTAL)
        self.glissando_rate_slider.pack(fill=tk.X, padx=int(self.master.winfo_screenwidth() * 0.2))
        ttk.Label(self.master, text="").pack()
        ttk.Label(self.master, text="").pack()
        ttk.Label(self.master, text="").pack()

        # Glissando direction selection with Radio Buttons
        ttk.Label(self.master, text="Trend of Shepard Tone").pack()
        self.radio_frame = tk.Frame(self.master)
        self.radio_frame.pack()
        self.asc_radio = ttk.Radiobutton(
            self.radio_frame, text="Ascending", variable=self.direction, value="Ascending")
        self.desc_radio = ttk.Radiobutton(
            self.radio_frame, text="Descending", variable=self.direction, value="Descending")
        self.asc_radio.pack(side=tk.LEFT, padx=10)
        self.desc_radio.pack(side=tk.LEFT, padx=10)
        ttk.Label(self.master, text="").pack()
        ttk.Label(self.master, text="").pack()
        ttk.Label(self.master, text="").pack()

        # Quit button
        self.quit_button = ttk.Button(
            self.master, text="Quit", command=self.quit)
        self.quit_button.pack()

    def setup_audio(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=1,
                                  rate=self.sample_rate,
                                  output=True)

    def setup_plot(self):
        # Initialize matplotlib plot for waveform and spectrum
        self.fig, (self.ax_waveform, self.ax_spectrum) = plt.subplots(2, 1, figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack()
        # Waveform plot
        self.ax_waveform.set_title("Time Domain Signal")
        self.ax_waveform.set_xlim(0, self.frames_per_buffer)
        self.ax_waveform.set_ylim(-1, 1)
        self.line_waveform, = self.ax_waveform.plot([], [], lw=1)
        # Spectrum plot
        self.ax_spectrum.set_title("Frequency Spectrum")
        self.ax_spectrum.set_xlim(0, 10000)
        self.ax_spectrum.set_ylim(0, 45)
        self.line_spectrum, = self.ax_spectrum.plot([], [], lw=1)
        plt.tight_layout()

    def update_plot(self, frame):
        # Update waveform plot
        self.line_waveform.set_data(np.arange(len(self.current_buffer)), self.current_buffer)
        # Compute and update spectrum plot
        spectrum = np.abs(fft(self.current_buffer)[:self.frames_per_buffer // 2])
        freqs = np.fft.fftfreq(self.frames_per_buffer, 1 / self.sample_rate)[:self.frames_per_buffer // 2]
        self.line_spectrum.set_data(freqs, spectrum)
        self.canvas.draw()
        return self.line_waveform, self.line_spectrum

    def audio_loop(self):
        if not self.is_running:
            return

        # Read parameters from sliders
        base_freq = self.base_frequency.get()
        volume = self.volume.get()
        direction = self.direction.get()
        num_octaves = self.num_octaves
        tones_per_octave = self.tones_per_octave
        rate = self.glissando_rate.get()
        # Generate time array for the current buffer
        frames = self.frames_per_buffer
        t_buffer = np.arange(frames) / self.sample_rate
        current_time = self.global_time + t_buffer
        buffer = np.zeros(frames)
        # Calculate frequencies, phases, and amplitudes
        if direction == "Ascending":
            positions = (np.outer(self.initial_positions, np.ones(
                frames)) + rate * current_time) % 1.0
        else:
            positions = (np.outer(self.initial_positions, np.ones(
                frames)) - rate * current_time) % 1.0

        freqs = base_freq * 2 ** (positions * num_octaves)
        amplitudes = np.exp(-0.5 * ((positions - 0.5) / 0.18) ** 2)
        delta_phases = 2 * np.pi * freqs / self.sample_rate

        # Accumulate phases and generate audio signals
        for i in range(self.num_tones):
            phase = self.phases[i]
            phase_increments = delta_phases[i]
            phases = phase + np.cumsum(phase_increments)
            self.phases[i] = phases[-1] % (2 * np.pi)
            buffer += amplitudes[i] * np.sin(phases)

        # Normalize buffer
        buffer /= self.num_tones
        buffer *= volume
        self.global_time += frames / self.sample_rate
        # Save current buffer for visualization
        self.current_buffer = buffer.copy()
        audio_data = buffer.astype(np.float32).tobytes()
        self.stream.write(audio_data)

        # Save audio data for WAV file
        if self.is_recording:
            wav_data = (buffer * 32767).astype(np.int16)
            self.audio_frames.append(wav_data.tobytes())

        # Schedule next audio loop
        self.master.after(1, self.audio_loop)

    def quit(self):
        self.is_running = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.save_wav_file("Shepard–Risset_Glissando.wav")
        self.master.destroy()

    def save_wav_file(self, filename):
        if not self.audio_frames:
            return

        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(self.audio_frames))
        wf.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = ShepardRissetApp(root)
    root.mainloop()
