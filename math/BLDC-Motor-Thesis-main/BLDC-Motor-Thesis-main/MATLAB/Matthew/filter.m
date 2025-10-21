format long g

omega = out.omega(end);

state1_tau = -1*mean(out.tau_state_1(end-5:end))*omega;
state2_tau = -1*mean(out.tau_state_2(end-5:end))*omega;
state3_tau = -1*mean(out.tau_state_3(end-5:end))*omega;
state4_tau = -1*mean(out.tau_state_4(end-5:end))*omega;
state5_tau = -1*mean(out.tau_state_5(end-5:end))*omega;
state6_tau = -1*mean(out.tau_state_6(end-5:end))*omega;
% state2_tau = -1*out.tau_state_2(end)*omega;
% state3_tau = -1*out.tau_state_3(end)*omega;
% state4_tau = -1*out.tau_state_4(end)*omega;
% state5_tau = -1*out.tau_state_5(end)*omega;
% state6_tau = -1*out.tau_state_6(end)*omega;
% mean(array(end-99:end))