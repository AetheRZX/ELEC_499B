clc;
%% 0. Grab logsout and yout
logsout_ds = [];
if exist('out','var') && isa(out, 'Simulink.SimulationOutput')
    if isprop(out,'logsout'), logsout_ds = out.logsout; end
    if isprop(out,'yout'), yout_ds = out.yout; else, yout_ds = []; end
elseif exist('logsout','var')
    logsout_ds = logsout;
    yout_ds = [];
end

if isempty(logsout_ds)
    error('No logged Dataset found (logsout). Run simulation first.');
end

%% 1. Extract Signals
get_sig_safe = @(ds, name) get_safe(ds, name);

% --- Currents ---
i_a = get_sig_safe(logsout_ds, 'i_a'); 
if isempty(i_a), i_a = get_sig_safe(logsout_ds, 'i_as'); end
i_b = get_sig_safe(logsout_ds, 'i_b');
i_c = get_sig_safe(logsout_ds, 'i_c');
i_ds = get_sig_safe(logsout_ds, 'i_ds');

% Handle the typo "avs"
i_ds_avg = get_sig_safe(logsout_ds, 'i_ds_avg'); 
if isempty(i_ds_avg), i_ds_avg = get_sig_safe(logsout_ds, 'i_ds_avs'); end

% --- Voltage / Back EMF ---
e_a = get_sig_safe(logsout_ds, 'e_a');
if isempty(e_a), e_a = get_sig_safe(logsout_ds, 'e_as'); end 
if isempty(e_a), e_a = get_sig_safe(logsout_ds, 'BackEmf'); end
e_q = get_sig_safe(logsout_ds, 'e_q');

% --- Mechanical ---
omega_r = get_sig_safe(logsout_ds, 'omega_r');
rotor_speed = get_sig_safe(logsout_ds, 'rotor speed');
theta_r = get_sig_safe(logsout_ds, 'theta_r');
T_e = get_sig_safe(logsout_ds, 'T_e');

% --- ISR / Digital Signals ---
hardware_ISR = get_sig_safe(logsout_ds, 'hardware_ISR');
software_ISR = get_sig_safe(logsout_ds, 'software_ISR');

% --- HALL STATES (ADDED) ---
perfect_hall = get_sig_safe(logsout_ds, 'perfect_hall_state');
result_hall  = get_sig_safe(logsout_ds, 'result_state');

% --- Fallback: Check "yout" (Outports) if logsout missed them ---
if ~isempty(yout_ds)
    if isempty(i_a), i_a = get_sig_safe(yout_ds, 'i_a'); end
    % ... (other fallbacks)
    if isempty(perfect_hall), perfect_hall = get_sig_safe(yout_ds, 'perfect_hall_state'); end
    if isempty(result_hall), result_hall = get_sig_safe(yout_ds, 'result_state'); end
end

% --- DEBUG SECTION ---
missing_signals = {};
if isempty(perfect_hall), missing_signals{end+1} = 'perfect_hall_state'; end
if isempty(result_hall), missing_signals{end+1} = 'result_state'; end

if ~isempty(missing_signals)
    fprintf('\n!!! WARNING: SIGNALS MISSING !!!\n');
    fprintf('Could not find: %s\n', strjoin(missing_signals, ', '));
    fprintf('Check your Simulink logging names.\n\n');
else
    fprintf('All critical signals found.\n');
end

%% 2. Save to .mat
tag = input('Enter run tag (e.g. "Hall_Test"): ', 's');
if isempty(tag), tag = 'Hall_Data'; end

data_struct = struct();

% Determine master time vector
if ~isempty(i_a)
    data_struct.time = i_a.Time;
elseif ~isempty(perfect_hall)
    data_struct.time = perfect_hall.Time;
end

% Pack data
if ~isempty(i_a), data_struct.i_a = i_a.Data; end
if ~isempty(omega_r), data_struct.omega_r = omega_r.Data; end
if ~isempty(T_e), data_struct.T_e = T_e.Data; end

% Pack Hall Data
if ~isempty(perfect_hall), data_struct.perfect_hall = perfect_hall.Data; end
if ~isempty(result_hall), data_struct.result_hall = result_hall.Data; end

current_script_path = fileparts(mfilename('fullpath'));
if isempty(current_script_path), current_script_path = pwd; end
output_dir = fullfile(current_script_path, 'mat_files_v2'); % Using v2 folder
if ~exist(output_dir, 'dir'), mkdir(output_dir); end

fname = fullfile(output_dir, sprintf('%s.mat', tag));
save(fname, '-struct', 'data_struct');
fprintf('Saved data to: %s\n', fname);

%% Helper Function
function val = get_safe(ds, name)
    try
        if isempty(ds), val = []; return; end
        elem = ds.find(name);
        if isempty(elem)
            val = [];
        else
            if numel(elem) > 1, elem = elem(1); end
            val = elem.Values;
        end
    catch
        val = [];
    end
end