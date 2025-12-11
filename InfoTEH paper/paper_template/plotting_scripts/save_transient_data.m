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

% Try logsout first
i_a = get_sig_safe(logsout_ds, 'i_a'); if isempty(i_a), i_a = get_sig_safe(logsout_ds, 'i_as'); end
i_ds = get_sig_safe(logsout_ds, 'i_ds');
i_ds_avg = get_sig_safe(logsout_ds, 'i_ds_avg');
theta_r = get_sig_safe(logsout_ds, 'theta_r');

% Back EMF
e_as = get_sig_safe(logsout_ds, 'e_as'); if isempty(e_as), e_as = get_sig_safe(logsout_ds, 'e_a'); end
if isempty(e_as), e_as = get_sig_safe(logsout_ds, 'BackEmf'); end
e_q = get_sig_safe(logsout_ds, 'e_q');

% Torque
T_e = get_sig_safe(logsout_ds, 'T_e');

% Try yout if missing
if isempty(i_ds) && ~isempty(yout_ds)
    i_ds = get_sig_safe(yout_ds, 'i_ds');
    fprintf('Checking yout for i_ds...\n');
end
if isempty(i_ds_avg) && ~isempty(yout_ds)
    i_ds_avg = get_sig_safe(yout_ds, 'i_ds_avg');
end
if isempty(T_e) && ~isempty(yout_ds)
    T_e = get_sig_safe(yout_ds, 'T_e');
end

% --- DEBUG SECTION ---
if isempty(i_ds) || isempty(i_ds_avg) || isempty(e_q) || isempty(T_e)
    fprintf('\n!!! SIGNALS MISSING !!!\n');
    fprintf('Check: i_ds, i_ds_avg, e_q, T_e.\n');
    fprintf('They were not found in "logsout".\n');
    fprintf('Please go to Simulink, RIGHT CLICK the "i_ds", "i_ds_avg", "e_q", "T_e" lines, and select "Log Selected Signals".\n');
    fprintf('Then re-run the simulation.\n\n');
    
    if ~isempty(yout_ds)
        fprintf('Available signals in "yout" (Port outputs):\n');
        for k = 1:yout_ds.numElements
            elem = yout_ds.get(k);
            fprintf('  %d) "%s"\n', k, elem.Name);
        end
    end
end

%% 2. Save
tag = input('Enter run tag (e.g. "lut0" or "lut1"): ', 's');
if isempty(tag), tag = 'default'; end

data_struct = struct();
if ~isempty(i_a), data_struct.i_a = i_a.Data; data_struct.time = i_a.Time; end
if ~isempty(i_ds), data_struct.i_ds = i_ds.Data; end
if ~isempty(i_ds_avg), data_struct.i_ds_avg = i_ds_avg.Data; end
if ~isempty(theta_r), data_struct.theta_r = theta_r.Data; end
if ~isempty(e_as), data_struct.e_as = e_as.Data; end
if ~isempty(e_q), data_struct.e_q = e_q.Data; end
if ~isempty(T_e), data_struct.T_e = T_e.Data; end

current_script_path = fileparts(mfilename('fullpath'));
if isempty(current_script_path), current_script_path = pwd; end
output_dir = fullfile(current_script_path, 'mat_files');
if ~exist(output_dir, 'dir'), mkdir(output_dir); end

fname = fullfile(output_dir, sprintf('transient_run_%s.mat', tag));
save(fname, '-struct', 'data_struct');
fprintf('Saved data to: %s\n', fname);


function val = get_safe(ds, name)
    try
        if isempty(ds), val = []; return; end
        val = ds.get(name).Values;
    catch
        val = [];
    end
end
