import scipy.io
import numpy as np

FILE = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files\LUT_torque_step_0_1_1s.mat"
data = scipy.io.loadmat(FILE)

t = data['time'].flatten()
print(f"Time Range: {t[0]:.4f} to {t[-1]:.4f}")

keys = [k for k in data.keys() if not k.startswith('__')]
print("Keys:", keys)

if 'omega_r' in data:
    w = data['omega_r'].flatten()
    print(f"Omega Range: {np.min(w):.2f} to {np.max(w):.2f}")
    
# Check for sharp drop to find step time
if 'omega_r' in data:
    dw = np.diff(w)
    idx = np.argmax(np.abs(dw))
    print(f"Max speed change at t={t[idx]:.4f}")
