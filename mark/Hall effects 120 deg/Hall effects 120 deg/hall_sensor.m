function [H1,H2,H3] = hall_sensor(theta_r, hall_errors)
%HALL_SENSOR Obtain hall signals from electrical angle
%   Detailed explanation goes here
H1 = 0;
H2 = 0;
H3 = 0;
theta_r1 = mod(theta_r - hall_errors(1), 2*pi);
theta_r2 = mod(theta_r - hall_errors(2), 2*pi);
theta_r3 = mod(theta_r - hall_errors(3), 2*pi);

if ((0 <= theta_r1 && theta_r1 <= pi/2) || (3*pi/2 <= theta_r1 &&  theta_r1 <=2*pi))
    H1 = 1;
end
if (pi/6 <= theta_r2 && theta_r2 <=7*pi/6)
    H2 = 1;
end
if (5*pi/6 <= theta_r3 && theta_r3 <=11*pi/6)
    H3 = 1;
end
end

