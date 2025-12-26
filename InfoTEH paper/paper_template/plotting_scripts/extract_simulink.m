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
% Fallback: sometimes named 'i_as' or 'i_a [A]'
if isempty(i_a), i_a = get_sig_safe(logsout_ds, 'i_as'); end

i_b = get_sig_safe(logsout_ds, 'i_b');
i_c = get_sig_safe(logsout_ds, 'i_c');

i_ds = get_sig_safe(logsout_ds, 'i_ds');
% Handle the typo "avs" seen in your screenshot
i_ds_avg = get_sig_safe(logsout_ds, 'i_ds_avg'); 
if isempty(i_ds_avg), i_ds_avg = get_sig_safe(logsout_ds, 'i_ds_avs'); end

% --- Voltage / Back EMF ---
% Primary goal: get e_a
e_a = get_sig_safe(logsout_ds, 'e_a');
if isempty(e_a), e_a = get_sig_safe(logsout_ds, 'e_as'); end 
if isempty(e_a), e_a = get_sig_safe(logsout_ds, 'BackEmf'); end

% Also grab e_q just in case
e_q = get_sig_safe(logsout_ds, 'e_q');

% --- Mechanical ---
omega_r = get_sig_safe(logsout_ds, 'omega_r');
rotor_speed = get_sig_safe(logsout_ds, 'rotor speed');
theta_r = get_sig_safe(logsout_ds, 'theta_r');
T_e = get_sig_safe(logsout_ds, 'T_e');


% --- Fallback: Check "yout" (Outports) if logsout missed them ---
if ~isempty(yout_ds)
    if isempty(i_a), i_a = get_sig_safe(yout_ds, 'i_a'); end
    if isempty(i_b), i_b = get_sig_safe(yout_ds, 'i_b'); end
    if isempty(i_c), i_c = get_sig_safe(yout_ds, 'i_c'); end
    if isempty(e_a), e_a = get_sig_safe(yout_ds, 'e_a'); end
    if isempty(omega_r), omega_r = get_sig_safe(yout_ds, 'omega_r'); end
    if isempty(rotor_speed), rotor_speed = get_sig_safe(yout_ds, 'rotor speed'); end
end

% --- DEBUG SECTION ---
missing_signals = {};
if isempty(e_a), missing_signals{end+1} = 'e_a'; end
if isempty(omega_r), missing_signals{end+1} = 'omega_r'; end
if isempty(i_a), missing_signals{end+1} = 'i_a'; end

if ~isempty(missing_signals)
    fprintf('\n!!! WARNING: SIGNALS MISSING !!!\n');
    fprintf('Could not find: %s\n', strjoin(missing_signals, ', '));
    fprintf('Check your log names.\n\n');
else
    fprintf('All critical signals found.\n');
end

%% 2. Save to .mat
tag = input('Enter run tag (e.g. "run1"): ', 's');
if isempty(tag), tag = 'default'; end

data_struct = struct();

% Determine master time vector
if ~isempty(i_a)
    data_struct.time = i_a.Time;
elseif ~isempty(e_a)
    data_struct.time = e_a.Time;
end

% Pack data
if ~isempty(i_a), data_struct.i_a = i_a.Data; end
if ~isempty(i_b), data_struct.i_b = i_b.Data; end
if ~isempty(i_c), data_struct.i_c = i_c.Data; end
if ~isempty(e_a), data_struct.e_a = e_a.Data; end
if ~isempty(e_q), data_struct.e_q = e_q.Data; end
if ~isempty(omega_r), data_struct.omega_r = omega_r.Data; end
if ~isempty(rotor_speed), data_struct.rotor_speed = rotor_speed.Data; end
if ~isempty(theta_r), data_struct.theta_r = theta_r.Data; end
if ~isempty(T_e), data_struct.T_e = T_e.Data; end
if ~isempty(i_ds), data_struct.i_ds = i_ds.Data; end
if ~isempty(i_ds_avg), data_struct.i_ds_avg = i_ds_avg.Data; end

current_script_path = fileparts(mfilename('fullpath'));
if isempty(current_script_path), current_script_path = pwd; end
output_dir = fullfile(current_script_path, 'mat_files');
if ~exist(output_dir, 'dir'), mkdir(output_dir); end

fname = fullfile(output_dir, sprintf(tag));
save(fname, '-struct', 'data_struct');
fprintf('Saved data to: %s\n', fname);

%% Helper Function
function val = get_safe(ds, name)
    try
        if isempty(ds), val = []; return; end
        % "find" is robust for partial matches or different object types
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