% Read the wav file
[y, Fs] = audioread('sin_08_mono.wav');

% Create a time vector for plotting
t = (0:length(y)-1)/Fs;

% Plot the audio signal
figure;
plot(t, y);
xlabel('Time (seconds)');
ylabel('Amplitude');
title('8-bit Sine Wave Signal');
grid on;


% Verify actual quantization step size
step_size = diff(y);
unique_steps = unique(step_size);

% Display the quantization step sizes
disp('Quantization step sizes:');
disp(unique_steps);

% Calculate expected quantization step size
max_value = max(y);
min_value = min(y);
expected_step_size = (max_value - min_value) / 255;

% Display expected quantization step size
disp('Expected quantization step size:');
disp(expected_step_size);


% FFT to verify the spectrum
Y = fft(y);
N = length(Y);
Y_mag = abs(Y/N);
f = (0:N-1)*(Fs/N);

% Plot the frequency spectrum (Magnitude vs Frequency)
figure;
plot(f(1:N/2), Y_mag(1:N/2));
xlabel('Frequency (Hz)');
ylabel('Magnitude');
title('Frequency Spectrum of the 8-bit Sine Wave');
grid on;
xlim([0, Fs/2]);
