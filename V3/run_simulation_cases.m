%% run_simulation_cases.m
% Automates the 3 simulation runs required for "compare_strategies.m".
% 
% ASSUMPTIONS:
%   1. 'bldc_sim_combined_2024' is the model name.
%   2. Control flags:
%       - 'hall_errors_ON': 1 = Errors present
%       - 'use_hall_filter' (OR SIMILAR): Control variable for Filter (Set below)
%       - 'MTPA_master_gain': Gain for MTPA (0 = Off, >0 = On)
%
%   > Please CHECK the "Configuration" section below to match your actual model variables!

modelName = 'bldc_sim_combined_2024';

% Load Model
load_system(modelName);

%% 1. Uncompensated (Hall Errors ON, No Filter, No MTPA)
fprintf('Running Case 1: Uncompensated...\n');
assignin('base', 'hall_errors_ON', 1);
assignin('base', 'use_LUT', 0);         % Assuming 0 = Filter/NoLUT? Or No Filter?
% NOTE: If "use_LUT=0" enables the Filter, we need a way to DISABLE it for "Uncompensated".
% If there isn't a flag, maybe set 'tau_filter' to a very small value or 0?
% For now, I assume 'use_LUT=0' and we set a flag 'enable_filter=0' if it exists.
% If not, check if you can just set Hall Errors and NO Correction.
%
% Hypothetical Flags (CHANGE THESE):
assignin('base', 'enable_filter', 0);   % <--- CHECK THIS NAME
assignin('base', 'MTPA_master_gain', 0);

sim(modelName);
logsout_uncomp = logsout;
save('data_uncomp.mat', 'logsout_uncomp');

%% 2. Filter Only (Hall Errors ON, Filter ON, No MTPA)
fprintf('Running Case 2: Filter Only...\n');
assignin('base', 'hall_errors_ON', 1);
assignin('base', 'use_LUT', 0);       % Use Filter (not LUT)
assignin('base', 'enable_filter', 1); % <--- Enable Filter
assignin('base', 'MTPA_master_gain', 0);

sim(modelName);
logsout_filter = logsout;
save('data_filter.mat', 'logsout_filter');

%% 3. Filter + MTPA (Hall Errors ON, Filter ON, MTPA ON)
fprintf('Running Case 3: Filter + MTPA...\n');
assignin('base', 'hall_errors_ON', 1);
assignin('base', 'use_LUT', 0);       % Use Filter
assignin('base', 'enable_filter', 1); 
assignin('base', 'MTPA_master_gain', 3); % Enable MTPA

sim(modelName);
logsout_mtpa = logsout;
save('data_mtpa.mat', 'logsout_mtpa');

fprintf('All 3 cases run. You can now run "infoTEH_figure/compare_strategies.m".\n');
