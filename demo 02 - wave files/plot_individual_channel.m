% Read the 3-channel wav file
[y, Fs] = audioread('sin_01_tripleChannel.wav');

% Display basic information about the signal
disp('Number of Channels:');
disp(size(y, 2));
disp('Sampling Frequency (Fs):');
disp(Fs);
disp('Length of the signal (in samples):');
disp(length(y));

% Create a time vector for plotting (in seconds)
t = (0:length(y)-1)/Fs;

% Plot Channel 1
figure;
plot(t, y(:, 1));
xlabel('Time (seconds)');
ylabel('Amplitude');
title('Channel 1: 220 Hz Sine Wave');
grid on;

% Plot Channel 2
figure;
plot(t, y(:, 2));
xlabel('Time (seconds)');
ylabel('Amplitude');
title('Channel 2: 440 Hz Sine Wave');
grid on;

% Plot Channel 3
figure;
plot(t, y(:, 3));
xlabel('Time (seconds)');
ylabel('Amplitude');
title('Channel 3: 880 Hz Sine Wave');
grid on;
