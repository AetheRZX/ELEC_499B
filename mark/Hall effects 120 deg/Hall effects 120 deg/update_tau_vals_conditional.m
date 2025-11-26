function [tau_now_out, tau_next_out, update_now, update_next, tau_corr_out] = update_tau_vals_conditional(timer, tau_vec, tau_now, tau_next, tau_LUT_input, use_LUT)

    % Finding tau_corr
    if use_LUT == 1
        % lut_mode
        tau_corr = tau_LUT_input; 
    else
        % filter_mode 
        tau_corr = (1/3)*(4*tau_vec(1) - tau_vec(2) + 2*tau_vec(3) - 4*tau_vec(4) + 2*tau_vec(5));
    end

    % Output for debugging
    tau_corr_out = tau_corr;
    
    update_now = false;
    update_next = false;

    
    if timer <= tau_now
        tau_now_out = tau_now;           % Keep current schedule
        tau_next_out = timer + tau_corr; 
        update_next = true;
    else
        tau_now_out = timer + tau_corr;  % Schedule NOW based on calculated duration
        update_now = true;
        tau_next_out = tau_next;         % Keep the queue
    end
end