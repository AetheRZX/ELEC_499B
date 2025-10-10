function f_Hz = avg_freq(omega_r)
%AVG_FREQ Calculate the fundamental frequency corresponding to the running
% average window

%why over 3 window and not over 2pi
f_Hz = max(3*max(omega_r,1e-5)/pi, 1);
end

