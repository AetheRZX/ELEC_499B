% Define constants

rs = 0.69/2; % Winding resistance
Lls = 50e-6; % Leakage inductance
Lms = 0.375e-3; % Magnetizing inductance
Lss = Lls + 1.5*Lms; 
tau_s = Lss/rs; % Stator time constant
Jt = 1e-3; % Moment of inertia
Dm = 1e-4; % Damping coeff    
P = 8; % Number poles
torque_const = 0.0591; % [Nm/A]
lambda_m = torque_const/(3*P/4); % permanent magnet flux linkage

L_ss = 0.45e-3;
r_s = 0.15;
tau_s = L_ss/r_s;
P = 8;
lambda_m = 21.5e-3;
% define mechanical constants
J_t = 12e-4; %        total moment of inertia
D_m = 1e-3; %        damping coefficient (due to friction)
% T_m = 1; %        load torque

% lambda_m = 21.5e-3; % PM Magnet flux linkage
% 
% r_pp = 0.69; % resistance, phase to phase
% r_s = r_pp/2;
% L_pp = 0.733e-3; % inductance, phase to phase
% tau_s = 1.06e-3; % stator time constant
% L_ss = tau_s * r_s;
% P = 8;
% torque_const = 0.0591; % [Nm/A]

r_pp = 0.69; % resistance, phase to phase
r_s = r_pp/2;
L_pp = 0.733e-3; % inductance, phase to phase
tau_s = 1.06e-3; % stator time constant
L_ss = tau_s * r_s;
P = 8;
torque_const = 0.0591; % [Nm/A]
lambda_m = torque_const/(3*P/4); % permanent magnet flux linkage

% define mechanical constants
J_t = 1e-3; %        total moment of inertia
D_m = 1e-3; %        damping coefficient (due to friction)
T_m = 1e-3; %        load torque



R_vs = 1e6; % ghost resistance from switch to neutral 

% Assume misalignment is normally distributed RV
% HallError1 = abs(randn*3);
% WrappedHallError1 = wrapTo360(HallError1);
% HallError2 = randn*3;
% HallError3 = randn*3;
% 
% theta12 = HallError1 - HallError2;
% theta31 = HallError3 - HallError1;
% theta23 = HallError2 - HallError3;

% define electrical constants
V_bus = 12;
f_SW_Hz = 50e3;
R_dsON_Ohm = 1e-3;
