% datasheet specs
r_pp = 0.69; % resistance, phase to phase
r_s = r_pp/2;
L_pp = 0.733e-3; % inductance, phase to phase
% tau_s = 1.06e-3; % stator time constant
tau_s = 1.06e-3; % stator time constant
L_ss = tau_s * r_s;
P = 8;
torque_const = 0.0591; % [Nm/A]
lambda_m = torque_const/(3*P/4); % permanent magnet flux linkage

% Required:
%   L_ss:     stator qd-coord inductance
%   r_s:      stator resistance
%   tau_s:    stator time constant
%   P:        num of poles
%   lambda_m: flux linkage due to permanent magnet


% sim specs

% L_ls = 0.1; %       stator leakage inductance
% L_ms = 0.1; %       stator magnetic inductance
% L_ss = L_ls + (3/2)*L_ms; %       stator qd-coord inductance
% r_s = 0.1; %        stator resistance
% tau_s = L_ss/r_s; % stator time constant
% P_pairs = 8; %      num of pole pairs
% P = 2*P_pairs; %    num of poles
% lambda_m = 0.1; %   flux linkage due to permanent magnet