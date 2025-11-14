function [tau_now_out, tau_next_out, update_now, update_next, tau_corr_out] = update_tau_vals_conditional(timer, tau_vec, tau_now, tau_next)
%UPDATE_TAU_VVALS Summary of this function goes here
%   Detailed explanation goes here

% fprintf('\nSee timer = %f, tau1=%f, tau2=%f, tau3=%f', timer, tau_vec(1), tau_vec(2), tau_vec(3));

% tau_corr = (1/3)*(tau_vec(2) + 2*tau_vec(3));
tau_corr = (1/3)*(4*tau_vec(1) - tau_vec(2) +2*tau_vec(3) -4*tau_vec(4) + 2*tau_vec(5));
tau_corr_out = tau_corr;
update_now = false;
update_next = false;

if timer <= tau_now
    tau_now_out = tau_now;
    tau_next_out = timer + tau_corr;
    update_next = true;
else
    tau_now_out = timer + tau_corr;
    update_now = true;
    tau_next_out = tau_next;
end
end

