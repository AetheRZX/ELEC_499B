R_s = 0.7;
L_ss = 0.002;
lambda_m = 0.1;
P = 4;

J = 0.1;
D_m = 0.1;

tau_s = L_ss/R_s;

p = 4;

phi_A_deg = 9.0 * 0;
phi_B_deg = -1.0 * 0;
phi_C_deg = 7.0* 0;

% Convert to Radians for the Simulink model
phi_A_rad = phi_A_deg * pi/180;
phi_B_rad = phi_B_deg * pi/180;
phi_C_rad = phi_C_deg * pi/180;
Ts_motor = 1e-6;