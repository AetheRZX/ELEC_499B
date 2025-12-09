%% compare_strategies.m
% Generates the "Steady state of LUT + MTPA vs uncompensated vs LUT only" figure.
%
% USAGE:
%   1. Run simulation for "Uncompensated" -> save logsout as 'logsout_uncomp'
%   2. Run simulation for "Filter Only"   -> save logsout as 'logsout_filter'
%   3. Run simulation for "Filter + MTPA" -> save logsout as 'logsout_mtpa'
%   4. Run this script.
%
%   If variables are missing, it generates dummy data for visualization structure.

clc; close all;

%% 1. CONFIGURATION
% Motor Parameters (Must match your simulation)
Params.P        = 4;
Params.lambda_m = 0.015;
Params.Ld       = 0.0004;
Params.Lq       = 0.0004;

% Time Window for Steady State (s)
t_ss_start = 0.05; 
t_ss_end   = 0.066; % Plot ~16ms window (one electrical cycle is ~6ms at 1850rpm)

%% 2. LOAD DATA (Or Mock if missing)
datasets = {'logsout_uncomp', 'logsout_filter', 'logsout_mtpa'};
labels   = {'Uncompensated', 'Filter Only', 'Filter + MTPA'};
colors   = {'b', 'k', 'r'};
styles   = {'-', '--', '-'};

Results = struct();

for i = 1:3
    varName = datasets{i};
    matFile = ['data_' strrep(varName, 'logsout_', '') '.mat']; % e.g., data_uncomp.mat
    
    % Try to find variable in workspace
    if evalin('base', ['exist(''' varName ''', ''var'')'])
        ds = evalin('base', varName);
        fprintf('Loaded %s from Workspace.\n', varName);
        found = true;
    % Try to load from .mat file
    elseif exist(matFile, 'file')
        fprintf('Loading %s from file...\n', matFile);
        loaded = load(matFile);
        if isfield(loaded, varName)
            ds = loaded.(varName);
            found = true;
        else
            warning('File %s found but did not contain %s.', matFile, varName);
            found = false;
        end
    else
        found = false;
    end

    if found
        % Extract Signals
        ts_ia = ds.getElement('i_a').Values;
        ts_ib = ds.getElement('i_b').Values;
        ts_ic = ds.getElement('i_c').Values;
        ts_tr = ds.getElement('theta_r').Values;
        
        t = ts_ia.Time;
        i_a = ts_ia.Data;
        i_b = ts_ib.Data;
        i_c = ts_ic.Data;
        theta_r = interp1(ts_tr.Time, ts_tr.Data, t, 'linear', 'extrap');
        
        % Calculate DQ & Torque
        theta_e = mod(theta_r * Params.P, 2*pi);
        i_alpha = (2/3) * (i_a - 0.5*i_b - 0.5*i_c);
        i_beta  = (2/3) * (sqrt(3)/2*i_b - sqrt(3)/2*i_c);
        i_d =  i_alpha .* cos(theta_e) + i_beta .* sin(theta_e);
        i_q = -i_alpha .* sin(theta_e) + i_beta .* cos(theta_e);
        T_e = 1.5 * Params.P * (Params.lambda_m .* i_q + (Params.Ld - Params.Lq) .* i_d .* i_q);
        
        % Store
        Results(i).t  = t;
        Results(i).ia = i_a;
        Results(i).Te = T_e;
        Results(i).id = i_d;
        Results(i).iq = i_q;
        
        % Calculate Metrics (Ratio)
        idx = t > t(1)+1; % Use last part for avg if t_ss is specific
        if ~any(idx), idx = 1:length(t); end
        
        T_avg = mean(T_e(idx));
        I_rms = rms(i_a(idx));
        Results(i).Ratio = T_avg / I_rms;
        
    else
        fprintf('Metric: %s not found. Using dummy data.\n', varName);
        % Dummy sinusoids for visual check
        t = linspace(0, 0.1, 1000)';
        Results(i).t  = t;
        Results(i).ia = 10 * sin(2*pi*100*t + (i-1)*0.2);
        Results(i).Te = 1.5 + 0.2*sin(2*pi*600*t);
        Results(i).Ratio = 1.5 / (10/sqrt(2)) + i*0.01;
    end
end

%% 3. PLOTTING
figure('Name', 'Comparison', 'Color', 'w', 'Position', [100 100 600 800]);

% (a) Torque Te
ax1 = subplot(3,1,1); hold on;
% Plot Uncomp vs MTPA
plot(Results(1).t*1000, Results(1).Te, 'b-', 'LineWidth', 1.5);
plot(Results(3).t*1000, Results(3).Te, 'r-', 'LineWidth', 1.5);
ylabel('T_e (Nm)');
legend('T_e (Uncompensated)', 'T_e (Filter + MTPA)');
title('(a) Electromagnetic Torque');
grid on;
xlim([t_ss_start, t_ss_end]*1000);

% (b) Phase Current i_as
ax2 = subplot(3,1,2); hold on;
plot(Results(1).t*1000, Results(1).ia, 'b-', 'LineWidth', 1.5);
plot(Results(3).t*1000, Results(3).ia, 'r-', 'LineWidth', 1.5);
ylabel('i_{as} (A)');
legend('i_{as} (Uncompensated)', 'i_{as} (Filter + MTPA)');
title('(b) Phase Current');
grid on;

% (c) Torque/Ampere Ratio
ax3 = subplot(3,1,3); hold on;
% This is a scalar, plot as horizontal line
for i = [3, 2, 1] % Order: MTPA (Top), Filter, Uncomp (Bot)
    yval = Results(i).Ratio;
    plot([t_ss_start t_ss_end]*1000, [yval yval], 'Color', colors{i}, 'LineStyle', styles{i}, 'LineWidth', 2);
    text(t_ss_end*1000, yval, sprintf(' %.4f (%s)', yval, labels{i}), 'Color', colors{i}, 'VerticalAlignment', 'bottom');
end
ylabel('T_e / |i_{as,rms}|');
title('(c) Torque per Ampere Ratio');
grid on;
xlabel('Time (ms)');

linkaxes([ax1, ax2, ax3], 'x');
xlim([t_ss_start, t_ss_end]*1000);

warning('Ensure you update "t_ss_start" and "t_ss_end" to zoom into the correct steady-state window!');
