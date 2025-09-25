% Paper parameter
R_s = 0.15;
L_ss = 0.45e-3;
lambda_m = 21.5e-3;
P = 8;
J = 12e-4;
D_m = 1e-5;
tau_s = L_ss/R_s;

% J = 0.1;
% D_m = 0.001;

phi_A_deg = 9.0 * 0;
phi_B_deg = -1.0 * 0;
phi_C_deg = 7.0* 0;

% Convert to Radians for the Simulink model
phi_A_rad = phi_A_deg * pi/180;
phi_B_rad = phi_B_deg * pi/180;
phi_C_rad = phi_C_deg * pi/180;



Ts_motor = 1e-6;
Ke = 2;
Kt = P/2 * lambda_m;