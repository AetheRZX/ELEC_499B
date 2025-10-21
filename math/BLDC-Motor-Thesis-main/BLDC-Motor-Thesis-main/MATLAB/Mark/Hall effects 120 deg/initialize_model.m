
%%
% define motor constants
% Required:
%   L_ss:     stator qd-coord inductance
%   r_s:      stator resistance
%   tau_s:    stator time constant
%   P:        num of poles
%   lambda_m: flux linkage due to permanent magnet

M_2311P_specs;

% L_ls = 0.1; %       stator leakage inductance
% L_ms = 0.1; %       stator magnetic inductance
% L_ss = L_ls + (3/2)*L_ms; %       stator qd-coord inductance
% r_s = 0.1; %        stator resistance
% tau_s = L_ss/r_s; % stator time constant
% P_pairs = 8; %      num of pole pairs
% P = 2*P_pairs; %    num of poles
% lambda_m = 0.1; %   flux linkage due to permanent magnet

% define simulation conditions
hall_errors_ON = 1;
hall_errors = [0.05,-0.05,0.04];
control_mode = 0; %     0 = torque control ; 1 = speed control

% define simulation constants
R_vs = 1e6; % ghost resistance from switch to neutral 

% define mechanical constants
J_t = 1e-3; %        total moment of inertia
D_m = 1e-3; %        damping coefficient (due to friction)
T_m = 1e-3; %        load torque

% define electrical constants
V_bus = 12;
f_SW_Hz = 50e3;
R_dsON_Ohm = 1e-3;

% define control constants
theta_v = 0; %      advance firing angle
switch control_mode
    case 0
        % torque control tuning (not tuned)
        P_duty_cycle = 15;
        I_duty_cycle = 1000;
        D_duty_cycle = 1e-3;
    case 1
        % speed control tuning
        P_duty_cycle = 10;
        I_duty_cycle = 1e-3;
        D_duty_cycle = 1e-3;
end

% define target values
