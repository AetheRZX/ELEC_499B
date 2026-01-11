clc;
%% 0. Setup: Define Name Mappings
% FORMAT: name_map('Text_To_Find_In_Simulink_List') = 'Output_Filename';
name_map = containers.Map('KeyType', 'char', 'ValueType', 'char');

% --- USER CONFIGURATION START ---
% This maps the run name (e.g., "Run 2: ...") to your custom file name
name_map('Run 2:') = 'LUT_transient_voltage';
name_map('Run 3:') = '3_step_transient_voltage';
name_map('Run 4:') = '6_step_transient_voltage';
% --------------------------------

% Get all available runs currently in the Inspector
all_run_IDs = Simulink.sdi.getAllRunIDs();
fprintf('Found %d runs in history.\n', length(all_run_IDs));

found_count = 0;

% Loop through every run in history to find our targets
for i = 1:length(all_run_IDs)
    this_id = all_run_IDs(i);
    run_obj = Simulink.sdi.getRun(this_id);
    run_name = run_obj.Name;
    
    % Check if this run name contains any of our target keys
    target_keys = keys(name_map);
    matched_key = '';
    
    for k = 1:length(target_keys)
        key = target_keys{k};
        if contains(run_name, key)
            matched_key = key;
            break;
        end
    end
    
    % If we didn't find a match in the map, skip this run
    if isempty(matched_key)
        continue; 
    end
    
    output_name = name_map(matched_key);
    found_count = found_count + 1;
    fprintf('\nMATCH FOUND: "%s" (Internal ID: %d) -> Saving as "%s"\n', run_name, this_id, output_name);

    %% 1. Extract Signals
    % Export using the discovered ID
    logsout_ds = Simulink.sdi.exportRun(this_id);
    
    % Handle struct wrapper if present
    if isstruct(logsout_ds) && isfield(logsout_ds, 'logsout')
        logsout_ds = logsout_ds.logsout;
    end
    
    get_sig_safe = @(ds, name) get_safe(ds, name);
    
    % --- Currents ---
    i_a = get_sig_safe(logsout_ds, 'i_a'); 
    if isempty(i_a), i_a = get_sig_safe(logsout_ds, 'i_as'); end
    i_b = get_sig_safe(logsout_ds, 'i_b');
    i_c = get_sig_safe(logsout_ds, 'i_c');
    i_ds = get_sig_safe(logsout_ds, 'i_ds');
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
    
    % --- ISRs ---
    hardware_ISR = get_sig_safe(logsout_ds, 'hardware_ISR');
    software_ISR = get_sig_safe(logsout_ds, 'software_ISR');

    %% 2. Save to .mat
    data_struct = struct();
    
    % Determine master time vector
    if ~isempty(i_a), data_struct.time = i_a.Time;
    elseif ~isempty(e_a), data_struct.time = e_a.Time;
    elseif ~isempty(hardware_ISR), data_struct.time = hardware_ISR.Time;
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
    if ~isempty(hardware_ISR), data_struct.hardware_ISR = hardware_ISR.Data; end
    if ~isempty(software_ISR), data_struct.software_ISR = software_ISR.Data; end
    
    % Save
    output_dir = fullfile(pwd, 'mat_files');
    if ~exist(output_dir, 'dir'), mkdir(output_dir); end
    
    fname = fullfile(output_dir, output_name);
    save(fname, '-struct', 'data_struct');
    fprintf('Saved data to: %s.mat\n', fname);
end

if found_count == 0
    fprintf('\nWARNING: No matching runs found.\nCheck that your runs (Run 2, Run 3...) are visible in the Simulation Data Inspector.\n');
end

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