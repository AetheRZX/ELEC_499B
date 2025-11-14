%% ==============================================================
%  Hall Sensor LUT Calibration from Simulink Logged Data
%  - Uses: state_out (Hall state), tau_corr_now (s)
%  - Input: out.logsout or logsout (Dataset)
%  - Output: phi_corr_LUT (Nx1, rad) and Simulink.Parameter
% ==============================================================

clc;

%% 1. Get the logsout Dataset (works with out.logsout or logsout)

if exist('out','var') && isa(out, 'Simulink.SimulationOutput') && isprop(out,'logsout')
    logsout_ds = out.logsout;
elseif exist('logsout','var') && isa(logsout, 'Simulink.SimulationData.Dataset')
    logsout_ds = logsout;
else
    error(['No logged Dataset found.\n' ...
           'After running the model you should have either ''out.logsout'' or ''logsout'' in the workspace.']);
end

%% 2. Extract state_out and tau_corr_now timeseries

elemNames = logsout_ds.getElementNames;

% --- Hall state ---
if any(strcmp('state_out', elemNames))
    state_sig = logsout_ds.getElement('state_out');
else
    error('Could not find signal ''state_out'' in logsout. Available names: %s', strjoin(elemNames, ', '));
end

% --- tau_corr_now ---
if any(strcmp('tau_corr_now', elemNames))
    tau_sig = logsout_ds.getElement('tau_corr_now');
else
    error('Could not find signal ''tau_corr_now'' in logsout. Available names: %s', strjoin(elemNames, ', '));
end

state_ts = state_sig.Values;   % timeseries
tau_ts   = tau_sig.Values;     % timeseries

%% 3. Put everything on the SAME time base (state_out time)

t_state = state_ts.Time(:);          % time vector for state_out
state   = double(state_ts.Data(:));  % Hall state values

t_tau   = tau_ts.Time(:);
tau_raw = tau_ts.Data(:);
tau_raw = tau_raw(:);               % column

% Resample tau_corr onto the state_out time base
tau_corr = interp1(t_tau, tau_raw, t_state, 'previous', 'extrap');

% Adopt state_out time base
t = t_state;

fprintf('Lengths: t = %d, state = %d, tau_corr = %d\n', ...
        numel(t), numel(state), numel(tau_corr));

%% 4. Optional: electrical speed omega_e (future-proof)

have_omega_signal = any(strcmp('omega_e', elemNames));
omega_e_vec = [];

if have_omega_signal
    omega_sig   = logsout_ds.getElement('omega_e');
    omega_ts    = omega_sig.Values;
    t_omega     = omega_ts.Time(:);
    omega_raw   = omega_ts.Data(:);
    omega_raw   = omega_raw(:);
    omega_e_vec = interp1(t_omega, omega_raw, t, 'linear', 'extrap');
end

%% 5. Choose a steady-state window for calibration

% Ignore the initial transient – tweak this if needed:
t_start_steady = t(1) + 1.0;           % ignore first 1 second
idx_ss         = (t >= t_start_steady);

if ~any(idx_ss)
    error('Steady-state window empty. Decrease t_start_steady or run the sim longer.');
end

t_ss        = t(idx_ss);
state_ss    = state(idx_ss);
tau_corr_ss = tau_corr(idx_ss);

fprintf('tau_corr_ss range before wrapping: [%.4f  %.4f] s\n', ...
        min(tau_corr_ss), max(tau_corr_ss));

%% 6. Compute electrical speed omega_0

if have_omega_signal
    omega_0 = mean(omega_e_vec(idx_ss));        % rad/s
else
    % Estimate from Hall-state transitions
    k_change = find(diff(state_ss) ~= 0);
    if numel(k_change) < 7
        error('Not enough Hall transitions in steady state to estimate omega.');
    end
    t_change  = t_ss(k_change);
    dt_change = diff(t_change);

    Te_est  = 6 * mean(dt_change);              % electrical period (s)
    omega_0 = 2*pi / Te_est;                    % rad/s
end

fprintf('Estimated electrical speed omega_0 = %.3f rad/s (%.1f rpm_elec)\n', ...
        omega_0, omega_0*60/(2*pi));

%% 7. Wrap tau_corr into one Hall sector [0, T_s)

Ts_nom = (pi/3) / omega_0;   % ideal time for 60° electrical
tau_corr_wrap = mod(tau_corr_ss, Ts_nom);

fprintf('Ts_nom = %.6f s, tau_corr_wrap range: [%.6f  %.6f] s\n', ...
        Ts_nom, min(tau_corr_wrap), max(tau_corr_wrap));

%% 8. Build LUT: phi_corr = omega_0 * mean( tau_corr_wrap | state )

hall_states = unique(state_ss(:));        % whatever values you actually have
nStates     = numel(hall_states);

phi_LUT_rad = zeros(nStates,1);
phi_LUT_deg = zeros(nStates,1);

for k = 1:nStates
    s = hall_states(k);
    idx_s = (state_ss == s);

    if ~any(idx_s)
        warning('No samples found for Hall state value %g in steady-state window.', s);
        continue;
    end

    tau_mean_s     = mean(tau_corr_wrap(idx_s));   % seconds
    phi_LUT_rad(k) = omega_0 * tau_mean_s;         % radians
    phi_LUT_deg(k) = phi_LUT_rad(k) * 180/pi;      % degrees
end

disp('----------------------------------------------');
disp('Hall correction LUT (phi_corr per state, degrees):');
table(hall_states, phi_LUT_deg, 'VariableNames', {'HallState','phi_deg'})
disp('----------------------------------------------');

%% 9. Export as workspace variable and Simulink.Parameter

phi_corr_LUT = phi_LUT_rad;   % Nx1, radians

phi_corr_LUT_param = Simulink.Parameter(phi_corr_LUT);
phi_corr_LUT_param.CoderInfo.StorageClass = 'ExportedGlobal';

disp('Created phi_corr_LUT (rad) and phi_corr_LUT_param (Simulink.Parameter).');
