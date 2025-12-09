%% generate_bldc_plots.m
% Analyzes BLDC simulation data (logsout) and generates figures.
%
% USAGE:
%   1. Run your Simulink simulation to get 'logsout' (or 'out.logsout').
%   2. Ensure 'logsout' is in the MATLAB workspace.
%   3. Run this script.
%
% REQURED PARAMETERS:
%   Please verify the "Configuration" section below, specifically the Motor Parameters.

clc; close all;

%% ==============================================================
%  1. CONFIGURATION
% ==============================================================

% --- Motor Parameters (UPDATE THESE!) ---
% These are used to calculate Torque and Electrical Angle
Params.P        = 4;            % Number of Pole Pairs (Example: 4)
Params.lambda_m = 0.0215;        % Flux linkage (Wb) (Example: 0.015)
Params.Ld       = 0.0004;       % d-axis Inductance (H)
Params.Lq       = 0.0004;       % q-axis Inductance (H)

% --- Plotting Settings ---
Settings.LineWidth = 1.5;
Settings.FontSize  = 12;

%% ==============================================================
%  2. DATA EXTRACTION
% ==============================================================
fprintf('Extracting signals from logsout...\n');

if exist('out','var') && isa(out, 'Simulink.SimulationOutput') && isprop(out,'logsout')
    ds = out.logsout;
elseif exist('logsout','var') && isa(logsout, 'Simulink.SimulationData.Dataset')
    ds = logsout;
else
    error('Dataset `logsout` not found in workspace.');
end

% Helper to get timeseries
get_ts = @(name) ds.getElement(name).Values;

try
    % Adjust these names if your signal names differ!
    % Based on your "logsout contents" listing:
    ts.i_a          = get_ts('i_a');
    ts.i_b          = get_ts('i_b');
    ts.i_c          = get_ts('i_c');
    ts.theta_r      = get_ts('theta_r'); % Rotor position (mech rad)
    ts.omega_r      = get_ts('omega_r'); % Rotor speed (mech rad/s)
    
    % Try to get optional signals (Back EMF, Torque might need calc)
    try ts.e_a = get_ts('e_a'); catch, ts.e_a = []; end 
    
    % Hall signals (if available)
    try ts.hall = get_ts('H1'); catch, ts.hall = []; end 
    
    % Check for control signals if useful
    try ts.id_ref = get_ts('id_ref'); catch, ts.id_ref = []; end
    
    fprintf('Signals found: i_abc, theta_r, omega_r.\n');
catch ME
    error('Missing required signals: %s. Check signal logging names.', ME.message);
end

%% ==============================================================
%  3. CALCULATIONS
% ==============================================================

% Common Time Vector (resample everything to current time)
t = ts.i_a.Time;
i_a = ts.i_a.Data;
i_b = ts.i_b.Data;
i_c = ts.i_c.Data;

% Interpolate theta and omega to current time
theta_r = interp1(ts.theta_r.Time, ts.theta_r.Data, t, 'linear', 'extrap');
omega_r = interp1(ts.omega_r.Time, ts.omega_r.Data, t, 'linear', 'extrap');

% Electrical Angle & Speed
theta_e = mod(theta_r * Params.P, 2*pi);
omega_e = omega_r * Params.P;

% Park Transformation (abc -> dq)
% Ref: Stationary frame 'alpha-beta', then to rotating 'd-q'
% Assumes balanced system, i_a + i_b + i_c = 0
% Alpha-Beta:
i_alpha = (2/3) * (i_a - 0.5*i_b - 0.5*i_c);
i_beta  = (2/3) * (sqrt(3)/2*i_b - sqrt(3)/2*i_c);

% D-Q (d-axis aligned with rotor flux?)
% Standard Park: 
% i_d = i_alpha * cos(theta_e) + i_beta * sin(theta_e);
% i_q = -i_alpha * sin(theta_e) + i_beta * cos(theta_e);
% NOTE: Verify alignment convention (sine vs cosine). 
% If theta_e is 0 when A-axis aligns with d-axis:
i_d =  i_alpha .* cos(theta_e) + i_beta .* sin(theta_e);
i_q = -i_alpha .* sin(theta_e) + i_beta .* cos(theta_e);

% Electromagnetic Torque Calculation
% Te = 1.5 * P * (lambda_m * i_q + (Ld - Lq) * i_d * i_q)
T_e = 1.5 * Params.P * (Params.lambda_m .* i_q + (Params.Ld - Params.Lq) .* i_d .* i_q);

% Back-EMF Calculation (Estimate)
% e_a = lambda_m * omega_e * sin(theta_e) (approx shape)
% Or fundamental:
e_as = Params.lambda_m .* omega_e .* sin(theta_e); % Fundamental estimate
% Note: Real BLDC Back-EMF is trapezoidal. This is a sinusoidal approx for "Fundamental".

%% ==============================================================
%  4. PLOTTING
% ==============================================================

% --- FIGURE 1: Phase Alignment (Fundamental Current vs Back EMF) ---
% Mimics: "Alignment of the fundamental phase current and back emf"
figure('Name', 'Fig 1: Phase Alignment', 'Color', 'w');
% Zoom in on a specific window (e.g., 2 cycles)
% Find a window in the middle or where speed is non-zero
idx_zoom = find(t > t(end)*0.8 & t < t(end)*0.85); 
if isempty(idx_zoom), idx_zoom = 1:min(1000, length(t)); end

subplot(1,1,1);
yyaxis left
plot(t(idx_zoom)*1000, i_a(idx_zoom), 'b-', 'LineWidth', Settings.LineWidth); hold on;
% Calculate fundamental (simple filter or just use raw if smooth)
% [Using raw for now as i_as_fund usually implies filtering]
ylabel('Current (A)');
ylim([-1.2*max(abs(i_a)), 1.2*max(abs(i_a))]);

yyaxis right
plot(t(idx_zoom)*1000, e_as(idx_zoom), 'k--', 'LineWidth', Settings.LineWidth);
ylabel('Back EMF (V)');
ylim([-1.2*max(abs(e_as)), 1.2*max(abs(e_as))]);

xlabel('Time (ms)');
title('Phase Current i_{as} and Back-EMF e_{as}');
legend('i_{as}', 'e_{as}');
grid on; set(gca,'FontSize',Settings.FontSize);


% --- FIGURE 2: Transient / Modes (Id, Iq) ---
% Mimics: "Uncompensated <-> Filter <-> MTPA"
figure('Name', 'Fig 2: dq Currents', 'Color', 'w');

subplot(2,1,1);
plot(t*1000, i_d, 'r', 'LineWidth', 1); hold on;
plot(t*1000, i_q, 'b', 'LineWidth', 1);
ylabel('Currents (A)');
legend('i_d', 'i_q');
title('d-q Frame Currents');
grid on; set(gca,'FontSize',Settings.FontSize);

subplot(2,1,2);
plot(t*1000, T_e, 'k', 'LineWidth', 1);
ylabel('Torque (Nm)');
xlabel('Time (ms)');
title('Electromagnetic Torque');
grid on; set(gca,'FontSize',Settings.FontSize);


% --- FIGURE 3: Startup Transient ---
% Mimics: "Rotor speed, torque, currents waveform"
figure('Name', 'Fig 3: Startup Transient', 'Color', 'w');

ax1 = subplot(3,1,1);
plot(t*1000, omega_e, 'LineWidth', Settings.LineWidth);
ylabel('\omega_e (rad/s)');
title('Electrical Speed');
grid on;

ax2 = subplot(3,1,2);
plot(t*1000, T_e, 'LineWidth', Settings.LineWidth);
ylabel('T_e (Nm)');
title('Torque');
grid on;

ax3 = subplot(3,1,3);
plot(t*1000, i_a, 'LineWidth', Settings.LineWidth);
ylabel('Phase Current (A)');
xlabel('Time (ms)');
title('Phase A Current');
grid on;

linkaxes([ax1, ax2, ax3], 'x');


fprintf('Generated 3 Figures.\n');
