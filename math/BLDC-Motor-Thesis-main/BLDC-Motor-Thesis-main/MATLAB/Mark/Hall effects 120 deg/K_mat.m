function [fq,fd] = K_mat(fa,fb,fc,theta)
%K_MAT Convert from stator to qd rotor reference frame
%   Detailed explanation goes here
a = 2*pi/3;
K = (2/3)*[cos(theta), cos(theta-a), cos(theta+a);
           sin(theta), sin(theta-a), sin(theta+a)];
fs_vec = [fa, fb, fc]';
fqd_vec = K*fs_vec;
fq = fqd_vec(1);
fd = fqd_vec(2);
end

