import scipy.io
import numpy as np

FILE = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files\LUT_torque_step_0_1_1s.mat"
data = scipy.io.loadmat(FILE)

t = data['time'].flatten()
# Look for step around 1.0s
mask = (t > 0.9) & (t < 1.1)
t_sub = t[mask]

if 'omega_r' in data:
    w = data['omega_r'].flatten()[mask]
    dw = np.diff(w)
    idx = np.argmax(np.abs(dw))
    print(f"Max speed change in [0.9, 1.1] at t={t_sub[idx]:.4f}")
    
# Also check detection on full range just in case
w_full = data['omega_r'].flatten()
dw_full = np.diff(w_full)
idx_full = np.argmax(np.abs(dw_full))
print(f"Max speed change (Global) at t={t[idx_full]:.4f}")
