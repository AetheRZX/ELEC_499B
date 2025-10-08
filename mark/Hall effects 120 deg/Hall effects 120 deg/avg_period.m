function T_avg = avg_period(omega_r)
%AVG_FREQ Calculate the fundamental frequency corresponding to the running
% average window
T_avg = pi/(3*max(omega_r,1e-5));
end

