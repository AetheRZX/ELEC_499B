clc;

% --- CONFIGURATION ---
modelName = 'bldc_sim_combined_2024'; % <--- CHECK THIS NAME matches your file
load_system(modelName);

% Define the 3 Scenarios
% Format: Name, use_LUT value, filter_mode_var value
% use_LUT: 1 = Use LUT (ignore filter), 0 = Use Algo
% filter_mode_var: 0 = Quadratic, 1 = 3-step, 2 = 6-step

scenarios = struct();

% 1. LUT Scenario
scenarios(1).Name = 'LUT';
scenarios(1).use_LUT = 1;
scenarios(1).filter_mode = 0; % Logic doesn't matter here if LUT is active

% 2. 3-Step Scenario
scenarios(2).Name = '3_step';
scenarios(2).use_LUT = 0;
scenarios(2).filter_mode = 1;

% 3. 6-Step Scenario
scenarios(3).Name = '6_step';
scenarios(3).use_LUT = 0;
scenarios(3).filter_mode = 2;

% --- BATCH RUN LOOP ---
for k = 1:length(scenarios)
    scen = scenarios(k);
    fprintf('\n========================================\n');
    fprintf('Running Scenario: %s ...\n', scen.Name);
    
    % 1. Set Workspace Variables
    assignin('base', 'use_LUT', scen.use_LUT);
    assignin('base', 'filter_mode_var', scen.filter_mode);
    
    % 2. Run Simulation
    try
        simOut = sim(modelName, 'ReturnWorkspaceOutputs', 'on');
    catch ME
        fprintf('Error running simulation: %s\n', ME.message);
        continue;
    end
    
    % 3. Extract Signals (Your exact logic)
    fprintf('Extracting signals...\n');
    
    logsout_ds = [];
    if isprop(simOut, 'logsout'), logsout_ds = simOut.logsout; end
    
    if isempty(logsout_ds)
        % Fallback for older Simulink versions or different configs
        if isprop(simOut, 'yout'), yout_ds = simOut.yout; else, yout_ds = []; end
        logsout_ds = yout_ds; % Try using yout as source if logsout fails
    end

    if isempty(logsout_ds)
        fprintf('WARNING: No data found for scenario %s. Skipping save.\n', scen.Name);
        continue;
    end

    % Define extraction helper
    get_sig_safe = @(ds, name) get_safe_local(ds, name);

    % --- Extract ---
    i_a = get_sig_safe(logsout_ds, 'i_a'); 
    if isempty(i_a), i_a = get_sig_safe(logsout_ds, 'i_as'); end
    i_b = get_sig_safe(logsout_ds, 'i_b');
    i_c = get_sig_safe(logsout_ds, 'i_c');
    i_ds = get_sig_safe(logsout_ds, 'i_ds');
    i_ds_avg = get_sig_safe(logsout_ds, 'i_ds_avs');

    % Back EMF signal - just one phase
    e_a = get_sig_safe(logsout_ds, 'e_a');
    e_q = get_sig_safe(logsout_ds, 'e_q');

    % Speed and position
    omega_r = get_sig_safe(logsout_ds, 'omega_r');
    omega_sw = get_sig_safe(logsout_ds, 'omega_sw'); % Added omega_sw
    rotor_speed = get_sig_safe(logsout_ds, 'rotor speed');
    theta_r = get_sig_safe(logsout_ds, 'theta_r');
    
    % Torque
    T_e = get_sig_safe(logsout_ds, 'T_e');

    % ISR signals
    hardware_ISR = get_sig_safe(logsout_ds, 'hardware_ISR');
    software_ISR = get_sig_safe(logsout_ds, 'software_ISR');

    % --- 4. Pack Data Structure ---
    data_struct = struct();
    
    % Time vector
    if ~isempty(i_a), data_struct.time = i_a.Time;
    elseif ~isempty(e_a), data_struct.time = e_a.Time;
    elseif ~isempty(hardware_ISR), data_struct.time = hardware_ISR.Time;
    end
    
    % Pack fields
    if ~isempty(i_a), data_struct.i_a = i_a.Data; end
    if ~isempty(i_b), data_struct.i_b = i_b.Data; end
    if ~isempty(i_c), data_struct.i_c = i_c.Data; end
    if ~isempty(e_a), data_struct.e_a = e_a.Data; end
    if ~isempty(e_q), data_struct.e_q = e_q.Data; end
    if ~isempty(omega_r), data_struct.omega_r = omega_r.Data; end
    if ~isempty(omega_sw), data_struct.omega_sw = omega_sw.Data; end % Added omega_sw
    if ~isempty(rotor_speed), data_struct.rotor_speed = rotor_speed.Data; end
    if ~isempty(theta_r), data_struct.theta_r = theta_r.Data; end
    if ~isempty(T_e), data_struct.T_e = T_e.Data; end
    if ~isempty(i_ds), data_struct.i_ds = i_ds.Data; end
    if ~isempty(i_ds_avg), data_struct.i_ds_avg = i_ds_avg.Data; end
    if ~isempty(hardware_ISR), data_struct.hardware_ISR = hardware_ISR.Data; end
    if ~isempty(software_ISR), data_struct.software_ISR = software_ISR.Data; end
    
    % --- 5. Save File ---
    output_dir = fullfile(pwd, 'mat_files');
    if ~exist(output_dir, 'dir'), mkdir(output_dir); end
    
    % Naming Convention: {filter_name}_torque_transient.mat
    fname_str = sprintf('%s_torque_transient_MTPA_on', scen.Name);
    fname = fullfile(output_dir, fname_str);
    
    save(fname, '-struct', 'data_struct');
    fprintf('SUCCESS: Saved data to "%s.mat"\n', fname_str);
end

fprintf('\nAll scenarios completed successfully.\n');

% --- Local Helper Function ---
function val = get_safe_local(ds, name)
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