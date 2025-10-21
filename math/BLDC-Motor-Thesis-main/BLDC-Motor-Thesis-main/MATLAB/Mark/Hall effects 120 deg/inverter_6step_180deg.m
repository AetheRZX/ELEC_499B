function [v_as, v_bs, v_cs] = inverter_6step_180deg(H1,H2,H3, Vdc)
%INVERTER Summary of this function goes here
%   Detailed explanation goes here

S_vec = [0, 0, 0]';
HALL_STATE = 4*H1 + 2*H2 + H3;
if HALL_STATE > 6
    error("Invalid hall state!!")
end
switch HALL_STATE
    case 4 % State I
        S_vec(1) = 1;
    case 6 % State II
        S_vec(1) = 1;
        S_vec(2) = 1;
    case 2 % State III
        S_vec(2) = 1;
    case 3 % State IV
        S_vec(2) = 1;
        S_vec(3) = 1;
    case 1 % State V
        S_vec(3) = 1;
    case 5 % State VI
        S_vec(3) = 1;
        S_vec(1) = 1;
    otherwise
end
V_mat = (1/3)*[2, -1, -1;
              -1, 2, -1;
              -1, -1, 2];
vs_vec = Vdc*V_mat*S_vec;
v_as = vs_vec(1);
v_bs = vs_vec(2);
v_cs = vs_vec(3);
end

