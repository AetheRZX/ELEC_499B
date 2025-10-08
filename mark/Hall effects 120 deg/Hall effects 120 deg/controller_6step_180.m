function [HALL_STATE, T_vec] = controller_6step_180(H1,H2,H3)
%CONTROLLER_6STEP_180 Summary of this function goes here
%   Detailed explanation goes here

T_vec = zeros(6,1);
HALL_STATE = 4*H1 + 2*H2 + H3;
if HALL_STATE > 6
    error("Invalid hall state!!")
end
switch HALL_STATE
    case 4 % State I
        T_vec([1,5,6]) = 1;
    case 6 % State II
        T_vec([1,2,6]) = 1;
    case 2 % State III
        T_vec([2,4,6]) = 1;
    case 3 % State IV
        T_vec([2,3,4]) = 1;
    case 1 % State V
        T_vec([3,4,5]) = 1;
    case 5 % State VI
        T_vec([1,3,5]) = 1;
    otherwise
end
end

