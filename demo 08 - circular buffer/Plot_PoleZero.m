b0 = 1.0;
G = 0.8;
N = 2205;

% Define the numerator coefficients for the transfer function
numerator = [b0, zeros(1, N-1), G];

% Define the denominator coefficients (for a non-recursive filter, it's just 1)
denominator = 1;

% Plot pole-zero diagram
zplane(numerator, denominator);
title('Pole-Zero Plot of the Filter');
