theta12_measured = out.theta12_measured.Data(end);
theta31_measured = out.theta13_measured.Data(end);
theta23_measured = out.theta23_measured.Data(end);

Wrapped_theta12_measured = wrapTo360(theta12_measured);
