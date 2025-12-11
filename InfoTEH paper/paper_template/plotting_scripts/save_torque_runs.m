clc;

%% 0. Grab logsout
logsout_ds = [];
if exist('out','var') && isa(out, 'Simulink.SimulationOutput')
    if isprop(out,'logsout'), logsout_ds = out.logsout; end
elseif exist('logsout','var')
    logsout_ds = logsout;
end

if isempty(logsout_ds)
    error('No logged Dataset found (logsout). Run simulation first.');
end

%% 1. Extract Signals
get_sig_safe = @(ds, name) get_safe(ds, name);

% Torque and Current
% Torque and Current
T_e = get_sig_safe(logsout_ds, 'T_e');
% Try 'i_a' (Phase A) or 'i_as'
i_a = get_sig_safe(logsout_ds, 'i_a');
if isempty(i_a), i_a = get_sig_safe(logsout_ds, 'i_as'); end

if isempty(T_e) || isempty(i_a)
    fprintf('\n!!! SIGNALS MISSING !!!\n');
    fprintf('Check: "T_e" and "i_as" (or "i_a").\n');
    fprintf('Please confirm these are logged in Simulink.\n');
    return;
end

%% 2. Save
tag = input('Enter run tag (e.g. "uncomp", "lut", "mtpa"): ', 's');
if isempty(tag), tag = 'test'; end

data_struct = struct();
data_struct.T_e = T_e.Data;
data_struct.i_a = i_a.Data;
data_struct.time = i_a.Time; % Assume common time base (Simulink usually ensures this for logsout)

current_script_path = fileparts(mfilename('fullpath'));
if isempty(current_script_path), current_script_path = pwd; end
output_dir = fullfile(current_script_path, 'mat_files');
if ~exist(output_dir, 'dir'), mkdir(output_dir); end

fname = fullfile(output_dir, sprintf('torque_run_%s.mat', tag));
save(fname, '-struct', 'data_struct');
fprintf('Saved data to: %s\n', fname);

function val = get_safe(ds, name)
    val = [];
    % Iterate to find element by name to avoid Simulink warnings
    for i = 1:ds.numElements
        elem = ds.get(i);
        if strcmp(elem.Name, name)
            val = elem.Values;
            return;
        end
    end
end
