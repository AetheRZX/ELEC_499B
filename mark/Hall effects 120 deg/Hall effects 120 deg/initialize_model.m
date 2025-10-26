
%%
% define motor constants
% Required:
%   L_ss:     stator qd-coord inductance
%   r_s:      stator resistance
%   tau_s:    stator time constant
%   P:        num of poles
%   lambda_m: flux linkage due to permanent magnet

% M_2311P_specs;
Arrow_86EMB3S98F_specs;

% define simulation conditions
hall_errors_ON = 1;
hall_errors = (pi/180)*[-3,5,-4];
closed_loop = 0;
control_mode = 1; %     0 = torque control ; 1 = speed control

% define simulation constants
R_vs = 1e6; % ghost resistance from switch to neutral 

% define mechanical constants
J_t = 12e-4; %        total moment of inertia
D_m = 1e-3; %        damping coefficient (due to friction)
T_m = 1.53; %        load torque

% define electrical constants
V_bus = 36;
f_SW_Hz = 50e3;
R_dsON_Ohm = 1e-3;

% define control constants
theta_v = pi/6; %      advance firing angle
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
MTPA_master_gain = 3;

omega_min = 50;
% define target values