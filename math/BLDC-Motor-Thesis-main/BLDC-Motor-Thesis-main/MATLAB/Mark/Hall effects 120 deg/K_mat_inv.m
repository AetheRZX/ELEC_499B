function [fa,fb,fc] = K_mat_inv(fq,fd,theta)
%K_MAT_INV Convert from qd rotor reference frame to stator frame
%   Detailed explanation goes here
a = 2*pi/3;
K_inv = [cos(theta), sin(theta);
         cos(theta-a), sin(theta-a);
         cos(theta+a), sin(theta+a)];
fqd_vec = [fq; fd];
fs_vec = K_inv*fqd_vec;
fa = fs_vec(1);
fb = fs_vec(2);
fc = fs_vec(3);
end

