clc;

%% 1. Get the logsout Dataset
if exist('out','var') && isa(out, 'Simulink.SimulationOutput') && isprop(out,'logsout')
    logsout_ds = out.logsout;
elseif exist('logsout','var') && isa(logsout, 'Simulink.SimulationData.Dataset')
    logsout_ds = logsout;
else
    error('No logged Dataset found. Run simulation first.');
end

elemNames = logsout_ds.getElementNames;

%% 2. Extract Signals (State, Tau, and Speed)

% --- Hall state ---
if any(strcmp('state_out', elemNames))
    state_sig = logsout_ds.getElement('state_out');
else
    error('Could not find "state_out".');
end

% --- tau_corr_out ---
if any(strcmp('tau_corr_out', elemNames))
    tau_sig = logsout_ds.getElement('tau_corr_out');
else
    error('Could not find "tau_corr_out".');
end

% --- Speed (Prefer True Omega) ---
if any(strcmp('omega_r', elemNames))
    omega_sig = logsout_ds.getElement('omega_r');
    fprintf('Using TRUE speed (omega_r).\n');
elseif any(strcmp('omega_e', elemNames))
    omega_sig = logsout_ds.getElement('omega_e');
    warning('Using ESTIMATED speed (omega_e).');
else
    error('No speed signal found.');
end

state_ts = state_sig.Values;
tau_ts   = tau_sig.Values;
omega_ts = omega_sig.Values;

%% 3. Sync Time Bases
% We align everything to the State transitions timestamps

t = state_ts.Time(:);
state = double(state_ts.Data(:));

t_tau = tau_ts.Time(:);
tau_raw = tau_ts.Data(:);
% Align Tau to State (Previous value holds)
tau_vec = interp1(t_tau, tau_raw, t, 'previous', 'extrap');

t_omega = omega_ts.Time(:);
omega_raw = omega_ts.Data(:);
% Align Speed to State (Linear interpolation for best accuracy)
omega_vec = interp1(t_omega, omega_raw, t, 'linear', 'extrap');

%% 4. Steady-State Window
t_start_steady = t(1) + 1.0; 
idx_ss = (t >= t_start_steady);

if ~any(idx_ss)
    error('Steady-state window empty.');
end

state_ss = state(idx_ss);
tau_ss   = tau_vec(idx_ss);
omega_ss = omega_vec(idx_ss);

%% 5. Build LUT using Instantaneous Physics
% Phi = Tau * Omega

hall_states = unique(state_ss(:));
nStates     = numel(hall_states);

phi_LUT_rad = zeros(nStates,1);
phi_LUT_deg = zeros(nStates,1);

for k = 1:nStates
    s = hall_states(k);
    idx_s = (state_ss == s);

    if ~any(idx_s)
        continue;
    end

    % 1. Get all Tau samples for this state
    taus_k = tau_ss(idx_s);
    
    % 2. Get all Speed samples for this state
    omegas_k = omega_ss(idx_s);
    
    % 3. Calculate Instantaneous Angle for each occurrence
    %    This accounts for speed ripples.
    instant_angles = taus_k .* omegas_k;
    
    % 4. Average the ANGLES (not the times)
    phi_LUT_rad(k) = mean(instant_angles);
    phi_LUT_deg(k) = phi_LUT_rad(k) * 180/pi;
end

%% 6. Shift Logic (Disabled by default)
% phi_LUT_rad = circshift(phi_LUT_rad, 1);
% phi_LUT_deg = circshift(phi_LUT_deg, 1);

disp('----------------------------------------------');
disp('Hall correction LUT (Instantaneous Calculation):');
LUT_table = table(hall_states, phi_LUT_deg, ...
                  'VariableNames', {'HallState','phi_deg'})
disp('----------------------------------------------');

%% 7. Export and Save
phi_corr_LUT = phi_LUT_rad; 
phi_corr_LUT_param = Simulink.Parameter(phi_corr_LUT);
phi_corr_LUT_param.CoderInfo.StorageClass = 'ExportedGlobal';

save('Hall_LUT_Config.mat', 'phi_corr_LUT_param');
fprintf('Saved to Hall_LUT_Config.mat\n');