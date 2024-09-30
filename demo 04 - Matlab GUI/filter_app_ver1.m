function filter_app_ver2()
    % Create UI figure window
    fig = uifigure('Position', [100 100 800 500]);
    fig.Name = 'Filter GUI with Signal Display';
    gl = uigridlayout(fig, [2, 1]);

    % Create axes for displaying signals and frequency response
    axSignal = uiaxes(gl);
    title(axSignal, 'Input and Filtered Signal')
    xlabel(axSignal, 'Time')
    ylabel(axSignal, 'Amplitude')
    
    axFreqResponse = uiaxes(gl);
    title(axFreqResponse, 'Frequency Response (Magnitude)')
    xlabel(axFreqResponse, 'Frequency (Hz)')
    ylabel(axFreqResponse, 'Magnitude (dB)')
    
    % Create slider for cut-off frequency control
    slider = uislider(fig, 'Position', [100 20 600 3], ...
        'Limits', [0.01 0.99], ...
        'Value', 0.3, ...
        'ValueChangedFcn', @(sld, event) updatePlots(sld, axSignal, axFreqResponse));

    % Generate initial signal and plot when the GUI loads
    updatePlots(slider, axSignal, axFreqResponse);
end

function updatePlots(slider, axSignal, axFreqResponse)
    % Get the current cut-off frequency value from the slider
    fc = slider.Value;

    % Generate the input signal (e.g., sinusoidal + noise)
    N = 500;
    n = 1:N;
    x = sin(5*pi*n/N) + 0.5 * randn(1, N);  % Input signal

    % Apply low-pass Butterworth filter
    [b, a] = butter(4, fc);  % 4th order Butterworth filter
    y = filtfilt(b, a, x);   % Filtered signal

    % Plot input signal and filtered output signal
    plot(axSignal, n, x, 'b', n, y, 'r');  % Blue: Input, Red: Filtered
    legend(axSignal, 'Input Signal', 'Filtered Signal');
    title(axSignal, sprintf('Filtered Signal (Cut-off Frequency = %.3f)', fc));
    xlabel(axSignal, 'Time');
    ylabel(axSignal, 'Amplitude');
    
    % Compute and plot frequency response of the filter
    [h, w] = freqz(b, a, 1024);
    plot(axFreqResponse, w/pi, 20*log10(abs(h)));
    ylim(axFreqResponse, [-80 10]);  % Limit y-axis for better visualization
    title(axFreqResponse, 'Frequency Response');
    xlabel(axFreqResponse, 'Normalized Frequency (\times\pi rad/sample)');
    ylabel(axFreqResponse, 'Magnitude (dB)');
end
