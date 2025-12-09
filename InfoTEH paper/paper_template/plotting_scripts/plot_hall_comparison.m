clc; close all;

%% 0. Grab the logsout Dataset
if exist('out','var') && isa(out, 'Simulink.SimulationOutput') && isprop(out,'logsout')
    logsout_ds = out.logsout;
elseif exist('logsout','var') && isa(logsout, 'Simulink.SimulationData.Dataset')
    logsout_ds = logsout;
else
    error('No logged Dataset found. Run simulation first.');
end

%% 1. Extract Signals
get_sig = @(name) logsout_ds.get(name).Values;

try
    H1 = get_sig('H1'); H2 = get_sig('H2'); H3 = get_sig('H3');
    H1_i = get_sig('H1_ideal'); H2_i = get_sig('H2_ideal'); H3_i = get_sig('H3_ideal');
catch
    error('Signal extraction failed. Check signal names.');
end

%% 2. Slice Data (Steady State > 1.0s)
start_time = 1.0; 
idx_start = find(H1.Time > start_time, 1);
if isempty(idx_start), idx_start = 1; end

h1_data_scan = H1.Data(idx_start:end);
t_scan = H1.Time(idx_start:end);

edges = find(diff(h1_data_scan) > 0.5);
if length(edges) >= 3
    end_idx_rel = edges(3);
    t_end = t_scan(end_idx_rel) + 0.001; 
else
    t_end = t_scan(end); % Fallback
end

crop = @(ts) timeseries(ts.Data(ts.Time >= start_time & ts.Time <= t_end), ...
                        ts.Time(ts.Time >= start_time & ts.Time <= t_end));

H1_c = crop(H1); H2_c = crop(H2); H3_c = crop(H3);
H1_ic = crop(H1_i); H2_ic = crop(H2_i); H3_ic = crop(H3_i);

%% 3. Save Data for Python (Robust Path)
data_struct.time = H1_c.Time;
data_struct.H1 = H1_c.Data;
data_struct.H2 = H2_c.Data;
data_struct.H3 = H3_c.Data;
data_struct.H1_ideal = H1_ic.Data;
data_struct.H2_ideal = H2_ic.Data;
data_struct.H3_ideal = H3_ic.Data;

% Determine location of THIS script file to ensure folder is created here
current_script_path = fileparts(mfilename('fullpath'));
if isempty(current_script_path)
    % If run section-by-section without saving, fallback to pwd, but warn
    current_script_path = pwd;
    fprintf('Warning: Script path not detected (unsaved?). Using pwd: %s\n', pwd);
end

output_dir = fullfile(current_script_path, 'mat_files');
if ~exist(output_dir, 'dir')
    mkdir(output_dir);
end

output_filename = fullfile(output_dir, 'hall_data_extracted.mat');
save(output_filename, '-struct', 'data_struct');

fprintf('SUCCESS: Data saved to:\n%s\n', output_filename);
