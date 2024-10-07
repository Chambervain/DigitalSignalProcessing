
%% Digital Filter GUI - Elliptic Filter
% GUI to modify the cut-off frequency, passband deviation, and stopband deviation

function recursive_filters_demo
    % Create the figure window
    f = figure('Name', 'Elliptic Filter GUI', 'Position', [100, 100, 800, 500]);
    
    % Add axes for the frequency response plot, centered
    ax1 = axes('Position', [0.3 0.55 0.4 0.35]);
    xlabel('Frequency (normalized)');
    ylabel('Magnitude');
    title('Frequency response');
    
    % Define initial filter parameters (ensure Rs > Rp)
    fc = 0.2;
    Rp = 0.01;
    Rs = 0.05;

    % Plot the initial frequency response
    plot_frequency_response(ax1, fc, Rp, Rs);
    
    % Add a slider for the cut-off frequency, larger and centered
    uicontrol('Style', 'text', 'Position', [350, 180, 120, 20], 'String', 'Cut-off frequency', 'FontSize', 10);
    cutoff_slider = uicontrol('Style', 'slider', 'Min', 0.05, 'Max', 0.5, 'Value', fc, ...
        'Position', [320, 160, 160, 20], 'Callback', @(src, event) update_plot());
    
    % Add a slider for the passband ripple, larger and centered
    uicontrol('Style', 'text', 'Position', [350, 130, 120, 20], 'String', 'Passband deviation', 'FontSize', 10);
    passband_slider = uicontrol('Style', 'slider', 'Min', 0.001, 'Max', 0.03, 'Value', Rp, ...
        'Position', [320, 110, 160, 20], 'Callback', @(src, event) update_plot());
    
    % Add a slider for the stopband attenuation, larger and centered
    uicontrol('Style', 'text', 'Position', [350, 80, 120, 20], 'String', 'Stopband deviation', 'FontSize', 10);
    stopband_slider = uicontrol('Style', 'slider', 'Min', 0.03, 'Max', 0.1, 'Value', Rs, ...
        'Position', [320, 60, 160, 20], 'Callback', @(src, event) update_plot());
    
    % Nested function to update the frequency response plot when sliders are changed
    function update_plot
        fc = get(cutoff_slider, 'Value');
        Rp = get(passband_slider, 'Value');
        Rs = get(stopband_slider, 'Value');

        if Rs <= Rp
            Rs = Rp + 0.01;
            set(stopband_slider, 'Value', Rs);
        end
        plot_frequency_response(ax1, fc, Rp, Rs);
    end
end

% Function to plot the frequency response
function plot_frequency_response(ax, fc, Rp, Rs)
    [b, a] = ellip(4, Rp*100, Rs*100, fc);
    [H, om] = freqz(b, a);
    f = om / (2*pi);
    plot(ax, f, abs(H), 'b');
    ylim(ax, [0 1.2]);
    grid on;
end
