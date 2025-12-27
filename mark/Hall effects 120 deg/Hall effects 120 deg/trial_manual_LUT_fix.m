clc;
% clear variables; % Keep variables for Simulink

%% 0. Configuration
START_TIME = 1.3; % Steady state start time

%% 1. Get logsout
if exist('out','var') && isa(out, 'Simulink.SimulationOutput') && isprop(out,'logsout')
    logsout_ds = out.logsout;
elseif exist('logsout','var') && isa(logsout, 'Simulink.SimulationData.Dataset')
    logsout_ds = logsout;
else
    error('No logged Dataset found. Run simulation first.');
end

get_sig = @(ds, name) ds.getElement(name).Values;

%% 2. Extract Signals
try
    state_ts = get_sig(logsout_ds, 'state_out');
    
    % Try to get the specific LUT algo signal first
    try
        tau_ts = get_sig(logsout_ds, 'tau_corr_LUT_algo');
        fprintf('Using signal: tau_corr_LUT_algo\n');
    catch
        tau_ts = get_sig(logsout_ds, 'tau_corr_out');
        fprintf('Using signal: tau_corr_out\n');
    end
    
    omega_ts = get_sig(logsout_ds, 'omega_r');
catch
    error('Missing required signals (state_out, tau, or omega_r).');
end

% Synchronize time vectors to State timestamp
t = state_ts.Time;
state = double(state_ts.Data);

% Interpolate Tau and Omega to align with State timestamps
% 'previous' is critical for discrete signals
tau_vec = interp1(tau_ts.Time, tau_ts.Data, t, 'previous', 'extrap'); 
omega_vec = interp1(omega_ts.Time, omega_ts.Data, t, 'linear', 'extrap');

%% 3. Filter for Steady State
mask = t >= START_TIME;
t_win = t(mask);
state_win = state(mask);
tau_win = tau_vec(mask);
omega_win = omega_vec(mask);

%% 4. Calculate Discrete "Trigger" Angles
% Logic: At the rising edge of the sector, the controller samples Omega 
% and outputs Tau. So: Angle = Tau_Steady * Omega_Instant

change_indices = find(diff(state_win) ~= 0);

sector_data = cell(1, 6);

% Iterate through each sector event
for k = 1:length(change_indices)-1
    
    % The index where the new sector BEGINS
    idx_trigger = change_indices(k) + 1;
    
    % 1. Identify Sector ID
    s = state_win(idx_trigger);
    
    % Map 0-5 to 1-6
    if s == 0, s = 1;
    elseif s >= 0 && s <= 5, s = s + 1;
    end
    if s < 1 || s > 6, continue; end
    
    % 2. Get INSTANTANEOUS Speed at the trigger point
    % This is the "Discrete Speed" the controller saw
    omega_inst = omega_win(idx_trigger);
    
    % 3. Get STEADY Tau
    % We grab Tau from the middle of the sector to avoid edge glitches,
    % assuming it is constant for the whole sector.
    idx_next_trigger = change_indices(k+1);
    idx_mid = floor((idx_trigger + idx_next_trigger) / 2);
    tau_steady = tau_win(idx_mid);
    
    % 4. Calculate Angle
    % Angle = Speed_Trigger * Tau_Held * (180/pi)
    angle_val = (omega_inst * (180/pi)) * tau_steady;
    
    % Store
    sector_data{s} = [sector_data{s}; angle_val];
end

%% 5. Results
fprintf('\n----------------------------------------\n');
fprintf('| Sector | Median Angle (deg) | Count |\n');
fprintf('|--------|--------------------|-------|\n');

final_lut = zeros(1,6);

for s = 1:6
    vals = sector_data{s};
    if ~isempty(vals)
        % Median helps ignore any weird simulation initialization glitches
        avg_angle = median(vals);
        final_lut(s) = avg_angle;
        fprintf('|   %d    |      %7.3f       |  %3d  |\n', s, avg_angle, length(vals));
    else
        fprintf('|   %d    |        NaN         |   0   |\n', s);
    end
end
fprintf('----------------------------------------\n');
fprintf('Sum: %.3f deg\n', sum(final_lut));

%% 6. Generate C-Code Array
fprintf('\n>>> COPY PASTE THIS >>>\n');
fprintf('float lut_angles[6] = {');
fprintf('%.3f, ', final_lut(1:end-1));
fprintf('%.3f};\n', final_lut(end));