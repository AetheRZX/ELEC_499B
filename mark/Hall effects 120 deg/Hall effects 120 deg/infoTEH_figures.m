
%% Initialize model
% % M_2311P_specs;
% Arrow_86EMB3S98F_specs;
% 
% % define simulation conditions
% hall_errors_ON = 1;
% hall_errors = (pi/180)*[-3,5,-4];
% closed_loop = 0;
% control_mode = 1; %     0 = torque control ; 1 = speed control
% 
% % define simulation constants
% R_vs = 1e6; % ghost resistance from switch to neutral 
% 
% % define mechanical constants
% J_t = 12e-4; %        total moment of inertia
% D_m = 1e-3; %        damping coefficient (due to friction)
% T_m = 1.53; %        load torque
% 
% % define electrical constants
% V_bus = 36;
% f_SW_Hz = 50e3;
% R_dsON_Ohm = 1e-3;
% 
% % define control constants
% theta_v = pi/6; %      advance firing angle
% switch control_mode
%     case 0
%         % torque control tuning (not tuned)
%         P_duty_cycle = 15;
%         I_duty_cycle = 1000;
%         D_duty_cycle = 1e-3;
%     case 1
%         % speed control tuning
%         P_duty_cycle = 10;
%         I_duty_cycle = 1e-3;
%         D_duty_cycle = 1e-3;
% end
% 
% % define target values
% 
% %% Run and save simulation
% simOut = sim("Hall_sensor_120deg_filter_org.slx");


%%
load("infoTEH_data/simOut_Dec11_1.mat")
load("data/MTPA_curve.mat")
%%
simData = simOut.get("yout");
timeData = simOut.get("tout");

ia = simData{1}.Values.Data;
id = simData{7}.Values.Data;
id_avg = simData{8}.Values.Data;
ea = simData{6}.Values.Data;

%% TEST PLOT i_as fundamental
indices = (timeData >= 1) & (timeData <= 1.04);
time_vals = timeData(indices);
ia_vals = ia(indices);

fs = 1/1e-6;
% f_low = 130;
% f_high = f_low + 20;
f_cutoff = 400;

% Design a bandpass FIR filter
filter_order = 10000;     % Filter order
d = designfilt('lowpassfir', ...
               'FilterOrder', filter_order, ...
               'CutoffFrequency', f_cutoff, ...
               'SampleRate', fs);

filtered_signal = filtfilt(d.Coefficients, 1, ia_vals); % Use filter coefficients

% Plot original and filtered signals
t = time_vals;              % Time vector
figure(10);
clf;
hold on
plot(time_vals, ia_vals);
plot(time_vals, filtered_signal, "Color","r");
xlim([1.002, 1.03])
hold off;

%% FIGURE 1: before and after filter application
figure(1);
clf;


% Figure 1a (before and after filter application)

% indices_f1a = (timeData >= 0.4671) & (timeData <= 0.5368);
indices_f1a = (timeData >= 0.4831) & (timeData <= 0.5285);
time_f1a = timeData(indices_f1a);
time_f1a = 1e3*(time_f1a - time_f1a(1)); % zero and convert to ms
ia_f1a = ia(indices_f1a);
id_f1a = id(indices_f1a);
id_avg_f1a = id_avg(indices_f1a);

t = tiledlayout(2, 1, 'TileSpacing', 'compact', 'Padding', 'compact');

nexttile;
hold on
plot(time_f1a,ia_f1a,"Color","b","LineWidth",1.2)
plot(time_f1a,id_f1a,"Color","magenta","LineWidth",1.2)
plot(time_f1a,id_avg_f1a,"Color","r","LineWidth",1.2)
xlabel("time (ms)")
ylabel("Ampere")
xlim([time_f1a(1), time_f1a(end)])
text(43,17,"(a) Applying filter","FontName","Times New Roman","FontSize",12,"HorizontalAlignment","right")

% filter apply annotation
plot([17.44, 17.44],[-15,20],'k-.',"LineWidth",1)
text(17.44-0.2,18,"No filter \leftarrow", "FontName","Times New Roman", "HorizontalAlignment","right", "FontSize",12)
text(17.44+0.2,18,"\rightarrow Applied filter ", "FontName","Times New Roman", "FontSize",12)


% manual legend
plot([7,14],[-17,-17],"Color","b","LineWidth",1.5)
text(14+0.7,-17,"$i_{as}$","FontSize",12,"Interpreter","latex")

plot([20,27],[-17,-17],"Color","magenta","LineWidth",1.5)
text(27+0.7,-17,"$i_{ds}$","FontSize",12,"Interpreter","latex")

plot([34,41],[-17,-17],"Color","r","LineWidth",1.5)
text(41+0.7,-17,"$\bar{i}_{ds}$","FontSize",12,"Interpreter","latex")

% legend with arrow
text(3,-15.5,"$i_{as}$","Interpreter","latex","FontSize",14)
text(4,-14,"\rightarrow","Color","b","Rotation",45,"FontWeight","bold", FontSize=20)

text(6.75,15,"$i_{ds}$","Interpreter","latex","FontSize",14)
text(6.75,14,"\rightarrow","Color","magenta","Rotation",-90,"FontWeight","bold", FontSize=20)

text(31.05,5,"$\bar{i}_{ds}$","Interpreter","latex","FontSize",14)
text(31.5,4.5,"\rightarrow","Color","r","Rotation",-90,"FontWeight","bold", FontSize=20)


% leg = legend("$i_{as}$","$i_{ds}$","$\bar{i}_{ds}$");
% set(leg,'Interpreter','latex');
% set(leg,'FontSize',12);
hold off

% Figure 1b (before and after MTPA application)
indices_f1b = (timeData >= 0.678) & (timeData <= 0.7789);
time_f1b = timeData(indices_f1b);
time_f1b = 1e3*(time_f1b - time_f1b(1)); % zero and convert to ms
ia_f1b = ia(indices_f1b);
id_f1b = id(indices_f1b);
id_avg_f1b = id_avg(indices_f1b);

nexttile;
hold on
plot(time_f1b,ia_f1b,"Color","b","LineWidth",1.2)
plot(time_f1b,id_f1b,"Color","magenta","LineWidth",1.2)
plot(time_f1b,id_avg_f1b,"Color","r","LineWidth",1.2)
xlabel("time (ms)")
ylabel("Ampere")
xlim([time_f1b(1), time_f1b(end)])
text(98,17,"(b) Applying MTPA","FontName","Times New Roman","FontSize",12, "HorizontalAlignment","right")

% filter apply annotation
plot([23.2, 23.2],[-15,20],'k-.',"LineWidth",1)
text(23.2-0.5,18,"No MTPA \leftarrow", "FontName","Times New Roman", "HorizontalAlignment","right", "FontSize",12)
text(23.2+0.5,18,"\rightarrow Applied MTPA ", "FontName","Times New Roman", "FontSize",12)

% manual legend
plot([14,29],[-17,-17],"Color","b","LineWidth",1.5)
text(29+1,-17,"$i_{as}$","FontSize",12,"Interpreter","latex")

plot([43,58],[-17,-17],"Color","magenta","LineWidth",1.5)
text(58+1,-17,"$i_{ds}$","FontSize",12,"Interpreter","latex")

plot([77,92],[-17,-17],"Color","r","LineWidth",1.5)
text(92+1,-17,"$\bar{i}_{ds}$","FontSize",12,"Interpreter","latex")

% legend with arrow
% text(8,-11,"$i_{as}$","Interpreter","latex","FontSize",14)
% text(9,-10,"\rightarrow","Color","b","Rotation",45,"FontWeight","bold", FontSize=20)
% 
% text(5.26,15,"$i_{ds}$","Interpreter","latex","FontSize",14)
% text(6,14,"\rightarrow","Color","magenta","Rotation",-90,"FontWeight","bold", FontSize=30)
% 
% text(46.76,10,"$\bar{i}_{ds}$","Interpreter","latex","FontSize",14)
% text(48,9,"\rightarrow","Color","r","Rotation",-90,"FontWeight","bold", FontSize=50)



% leg = legend("$i_{as}$","$i_{ds}$","$\bar{i}_{ds}$","Location","southeast");
% set(leg,'Interpreter','latex');
% set(leg,'FontSize',12);
hold off
%% FIGURE 2: e_as and i_as alignment, initial, after filter, after MTPA
figure(2)
clf
% Figure 2a (initial)
indices_f2a = (timeData >= 0.2568) & (timeData <= 0.3021);
time_f2a = timeData(indices_f2a);
time_f2a = 1e3*(time_f2a - time_f2a(1)); % zero and convert to ms
ia_f2a = ia(indices_f2a);
ia_fund_f2a = filtfilt(d.Coefficients, 1, ia_f2a);
ea_f2a = ea(indices_f2a);

t = tiledlayout(3, 1, 'TileSpacing', 'compact', 'Padding', 'compact');

nexttile
hold on
plot(time_f2a,ia_f2a,"Color","b","LineWidth",1.2)
plot(time_f2a,ia_fund_f2a, "Color","r","LineWidth",1.2)
ylim([-20,20])
ylabel("Ampere")

text(8.2,-16,"(a) Initial, with Hall misalignments","FontName","Times New Roman", ...
    "FontSize", 12)

yyaxis right
plot(time_f2a, ea_f2a, "Color","k","LineWidth",1.2)
ylabel("e_{as} (V)")
xline(12.5,"k-.","LineWidth",1)
xline(12.624,"r-.","LineWidth",1)
xlim([8, 21.1])

ax = gca();
ax.YAxis(2).Color = [0 0 0];
% xticklabels(ax.XAxis.TickValues-8)

lg = legend("$i_{as}$","$i_{as-fund}$","$e_{as}$", "Location","southeast");
set(lg, "Interpreter", "latex")
set(lg,'FontSize',12);

% legend with arrow (for first plot only)
text(13.4,5,"$i_{as}$","Interpreter","latex","FontSize",12)
text(13.4,4,"\rightarrow","Color","b","Rotation",-90-45,"FontWeight","bold", FontSize=20)

 
text(17.15,16,"$e_{as}$","Interpreter","latex","FontSize",12)
text(17.3,15,"\rightarrow","Color","k","Rotation",-90,"FontWeight","bold", FontSize=20)

 
text(17.1,-2.5,"$i_{as-fund}$","Interpreter","latex","FontSize",12)
text(17.1,-1.5,"\rightarrow","Color","r","Rotation",90,"FontWeight","bold", FontSize=25)

hold off


% Figure 2b (after filter)
indices_f2b = (timeData >= 0.5966) & (timeData <= 0.6421);
time_f2b = timeData(indices_f2b);
time_f2b = 1e3*(time_f2b - time_f2b(1)); % zero and convert to ms
ia_f2b = ia(indices_f2b);
ia_fund_f2b = filtfilt(d.Coefficients, 1, ia_f2b);
ea_f2b = ea(indices_f2b);

nexttile
hold on
plot(time_f2b,ia_f2b,"Color","b","LineWidth",1.2)
plot(time_f2b,ia_fund_f2b, "Color","r","LineWidth",1.2)
ylim([-20,20])
ylabel("Ampere")

% draw delta_phi_v symbol
text(12.495, 15, "\rightarrow", "HorizontalAlignment","right", "FontSize",16)
text(12.694, 15, "$\leftarrow \Delta \phi_v$", "Interpreter","latex","FontSize",16)

text(8.2,-16,"(b) After filter, without MTPA","FontName","Times New Roman", ...
    "FontSize", 12)

yyaxis right
plot(time_f2b, ea_f2b, "Color","k","LineWidth",1.2)
ylabel("e_{as} (V)")
xline(12.495,"k-.","LineWidth",1)
xline(12.694,"r-.","LineWidth",1)
xlim([8, 21.1])

ax = gca();
ax.YAxis(2).Color = [0 0 0];
xticklabels(ax.XAxis.TickValues-8)

lg = legend("$i_{as}$","$i_{as-fund}$","$e_{as}$", "Location","southeast");
set(lg, "Interpreter", "latex")
set(lg,'FontSize',12);
hold off

% Figure 2c (after filter + MTPA)
indices_f2c = (timeData >= 1.3962) & (timeData <= 1.4409);
time_f2c = timeData(indices_f2c);
time_f2c = 1e3*(time_f2c - time_f2c(1)); % zero and convert to ms
ia_f2c = ia(indices_f2c);
ia_fund_f2c = filtfilt(d.Coefficients, 1, ia_f2c);
ea_f2c = ea(indices_f2c);


nexttile
hold on
plot(time_f2c,ia_f2c,"Color","b","LineWidth",1.2)
plot(time_f2c,ia_fund_f2c, "Color","r","LineWidth",1.2)
ylim([-20,20])
ylabel("Ampere")

text(12.42, 15, "\leftarrow MTPA compensated","FontSize",12, "FontName",'Times New Roman')
text(8.2,-16,"(c) Both filter and MTPA applied","FontName","Times New Roman", ...
    "FontSize", 12)

yyaxis right
plot(time_f2c, ea_f2c, "Color","k","LineWidth",1.2)
ylabel("e_{as} (V)")
xline(12.42,"k-.","LineWidth",1)
xline(12.42,"r-.","LineWidth",1)
xlim([8, 21])
xlabel("time (ms)")

ax = gca();
ax.YAxis(2).Color = [0 0 0];
xticklabels(ax.XAxis.TickValues-8)

lg = legend("$i_{as}$","$i_{as-fund}$","$e_{as}$", "Location","southeast");
set(lg, "Interpreter", "latex")
set(lg,'FontSize',12);
hold off


%% FIGURE 3 Plot compensated MTPA angles
figure(3)
clf
hold on
scatter(speed_avg_vals, phi_avg_vals, 20, 'r', 'filled')
% plot(speed_avg_vals, phi_avg_vals,'r-')
yline(30, 'b', 'LineWidth', 2);
xlim([700,2400])
ylim([28,44])
xlabel("n (rpm)")
ylabel("\phi_v (degrees)")
title("Compensated angle (MTPA)")
text(900,29.5,"Uncompensated $\phi _v = 30^\circ$","Interpreter","latex","FontSize",12)
text(1650,40.5,"Compensated $\phi_v'(\omega_r,\bar{v}_{dc})$","Interpreter","latex","FontSize",12)
legend(["MTPA (with filter)", "COM"],"Interpreter","latex")
annotation("doublearrow",[0.62,0.62], [0.22,0.65], "Color","r")
text(1750,35,"$\Delta\phi_v'(\omega_r,\bar{v}_{dc})$","Interpreter","latex","FontSize",12, ...
    "Color","r","HorizontalAlignment","right")
hold off

%% FIGURE 4 Plot MTPA without filter
% need to manually disable filter
simOut_f4 = sim("Hall_sensor_120deg_filter_org.slx");
%%
simData_f4 = simOut_f4.get("yout");
time_f4 = simOut_f4.get("tout");
ia_f4 = simData_f4{1}.Values.Data;
id_f4 = simData_f4{7}.Values.Data;
id_avg_f4 = simData_f4{8}.Values.Data;
del_phi_f4 = simData_f4{10}.Values.Data;
%%
indices_f4 = (time_f4 >= 0.678) & (time_f4 <= 0.7789);
time_f4_val = time_f4(indices_f4);
time_f4_val = 1e3*(time_f4_val - time_f4_val(1)); % zero and convert to ms
ia_f4 = ia_f4(indices_f4);
id_f4 = id_f4(indices_f4);
id_avg_f4 = id_avg_f4(indices_f4);
%%
figure(4);
clf;

hold on
plot(time_f4_val,ia_f4,"Color","b","LineWidth",1.2)
plot(time_f4_val,id_f4,"Color","magenta","LineWidth",1.2)
plot(time_f4_val,id_avg_f4,"Color","r","LineWidth",1.2)
xlabel("time (ms)")
ylabel("Ampere")
xlim([time_f4_val(1), time_f4_val(end)])
% text(98,17,"(b) Applying MTPA","FontName","Times New Roman","FontSize",12, "HorizontalAlignment","right")

% filter apply annotation
plot([23.2, 23.2],[-15,20],'k-.',"LineWidth",1)
text(23.2-0.5,18,"No MTPA \leftarrow", "FontName","Times New Roman", "HorizontalAlignment","right", "FontSize",12)
text(23.2+0.5,18,"\rightarrow Applied MTPA ", "FontName","Times New Roman", "FontSize",12)

% manual legend
plot([14,29],[-17,-17],"Color","b","LineWidth",1.5)
text(29+1,-17,"$i_{as}$","FontSize",12,"Interpreter","latex")

plot([43,58],[-17,-17],"Color","magenta","LineWidth",1.5)
text(58+1,-17,"$i_{ds}$","FontSize",12,"Interpreter","latex")

plot([77,92],[-17,-17],"Color","r","LineWidth",1.5)
text(92+1,-17,"$\bar{i}_{ds}$","FontSize",12,"Interpreter","latex")

% legend with arrow
annotation("arrow",[0.2,0.2+0.02],[0.2,0.2+0.02]+0.1,'Color', 'b', 'LineWidth', 1.5)
text(8,-11,"$i_{as}$","Interpreter","latex","FontSize",12)

annotation("arrow",[0.175,0.175],[0.4,0.4-0.04]+0.38,'Color', 'magenta', 'LineWidth', 1.5)
text(5.26,14,"$i_{ds}$","Interpreter","latex","FontSize",12)

annotation("arrow",[0.495,0.495],[0.55,0.55-0.25]+0.24,'Color', 'r', 'LineWidth', 1.5)
text(46.76,14.5,"$\bar{i}_{ds}$","Interpreter","latex","FontSize",12)
hold off





