
%%
% Specify error
% hall_errors = (pi/180)*([-3,5,-4]);
hall_errors = [0 0 0];

% Specify the range of torque values
torque_vals = linspace(0.1,9,20);
speed_avg_vals = zeros(length(torque_vals),1);
phi_avg_vals = zeros(length(torque_vals),1);
simResults = cell(length(torque_vals),1);

for i = 1:length(torque_vals)
    % set torque value
    T_m = torque_vals(i);
    fprintf("Running T_m = %.1f ....\n", T_m)
    % run simulation
    stopTime = 2.5;
    if i >= 9
        stopTime = 1.5;
    end
    simOut = sim("Hall_sensor_120deg_filter_org.slx","StopTime",sprintf("%f",stopTime));

    % get speed and del_phi data 
    simData = simOut.get("yout");
    speed_data = simData{4};
    del_phi_data = simData{10};
    
    % average over the last 0.2 s 
    index_marker = round((0.2/2.5)*length(speed_data.Values.Time));
    speed_avg = mean(speed_data.Values.Data(end-index_marker:end));
    del_phi_avg = mean(del_phi_data.Values.Data(end-index_marker:end));

    % print and store result
    speed_avg_vals(i) = speed_avg;
    phi_avg = (pi/6 + del_phi_avg) * 180/pi;
    phi_avg_vals(i) = phi_avg;
    
    fprintf("\nT_m = %.1f : n = %.0f ; phi = %.1f deg", T_m, speed_avg, phi_avg)
    % save(sprintf("data/T_m%.1f_n%.0f.mat", T_m, speed_avg), 'simOut');
    simResults{i} = simOut;
end

% save("data/data_12_02_24_testrun.mat","simResults");
save("infoTEH_data\MTPA_curve_perfect.mat","speed_avg_vals","phi_avg_vals")

% %%
% simOut = sim("Hall_sensor_120deg_filter_org.slx");
% 
% %%
% figure(1);
% simData = simOut.get("yout");
% data_ia = simData{1};
% plot(data_ia.Values.Time, data_ia.Values.Data)

%%
% figure(2)
% clf
% hold on
% scatter(speed_avg_vals, phi_avg_vals, 8, 'r', 'filled')
% yline(30, 'b', 'LineWidth', 2);
% xlim([700,2400])
% ylim([28,44])
% xlabel("n (rpm)")
% ylabel("\phi_v deg")
% title("Compensated angle (MTPA)")
% legend(["MTPA", "COM"])
% hold off



