import numpy as np
import scipy.io
import matplotlib.pyplot as plt
import os

# --- Configuration ---
DATA_DIR = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files"
OUTPUT_FILE = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\figures\4_torque_step.png"

FILES = [
    {'name': '3_step_torque_step_0_1_1s.mat', 'label': '3-step Averaging', 'color': '#0072BD'}, # Blue
    {'name': '6_step_torque_step_0_1_1s.mat', 'label': '6-step Averaging', 'color': '#D95319'}, # Red
    {'name': 'LUT_torque_step_0_1_1s.mat',    'label': 'LUT Correction',   'color': '#EDB120'}  # Yellow
]

POLE_PAIRS = 4

def derive_torque_active_power(d):
    # T = (3 * e_a * i_a) / (w_r / P)
    e_a = d['e_a']
    i_a = d['i_a']
    w_r = d['w_r']
    
    w_m = w_r / POLE_PAIRS
    T = np.zeros_like(e_a)
    
    # Avoid div by zero
    mask = np.abs(w_m) > 1.0 # 1 rad/s threshold
    T[mask] = (3.0 * e_a[mask] * i_a[mask]) / w_m[mask]
    return T

# --- Load Data ---
data_list = []
for f in FILES:
    path = os.path.join(DATA_DIR, f['name'])
    if not os.path.exists(path):
        print(f"File missing: {f['name']}")
        continue
    
    try:
        mat = scipy.io.loadmat(path)
        item = {'label': f['label'], 'color': f['color']}
        
        item['t'] = mat['time'].flatten()
        
        # Keys check
        if 'omega_r' in mat and 'i_a' in mat and 'e_a' in mat:
             item['w_r'] = mat['omega_r'].flatten()
             item['i_a'] = mat['i_a'].flatten()
             item['e_a'] = mat['e_a'].flatten()
             item['T_e'] = derive_torque_active_power(item)
        elif 'T_e' in mat:
             item['w_r'] = mat['omega_r'].flatten()
             item['T_e'] = mat['T_e'].flatten()
        else:
            print(f"Missing required keys in {f['name']}")
            continue

        data_list.append(item)
    except Exception as e:
        print(f"Error loading {f['name']}: {e}")

if not data_list:
    raise ValueError("No data loaded")

# --- Find Step Time around 1.0s ---
# Use LUT dataset
ref_data = data_list[-1] 
t = ref_data['t']
w = ref_data['w_r']

# Look in 0.9 to 1.1 region
mask_search = (t > 0.9) & (t < 1.1)
if not np.any(mask_search):
     print("Warning: No data in 0.9-1.1s. Finding global max.")
     mask_search = np.ones_like(t, dtype=bool)

t_sub = t[mask_search]
w_sub = w[mask_search]
dw = np.diff(w_sub)
step_idx = np.argmax(np.abs(dw))
step_time = t_sub[step_idx]
print(f"Detected step at t={step_time:.4f}s")

# Define Window: -5ms to +80ms from step
t_start = step_time - 0.005
t_end = step_time + 0.080

# --- Plotting ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6), sharex=True, constrained_layout=True)

for d in data_list:
    mask = (d['t'] >= t_start) & (d['t'] <= t_end)
    t_plot = d['t'][mask]
    w_plot = d['w_r'][mask]
    T_plot = d['T_e'][mask]
    
    if len(t_plot) == 0: continue

    # Relative time (ms) starting from 0 (where 0 corresponds to t_start)
    t_rel_ms = (t_plot - t_start) * 1000
    
    ax1.plot(t_rel_ms, w_plot, label=d['label'], color=d['color'], linewidth=1.5)
    ax2.plot(t_rel_ms, T_plot, label=d['label'], color=d['color'], linewidth=1.5)

# Dashed line at step
step_rel_ms = (step_time - t_start) * 1000
ax1.axvline(step_rel_ms, color='k', linestyle='--', alpha=0.6)
ax2.axvline(step_rel_ms, color='k', linestyle='--', alpha=0.6)

# Labels
ax1.set_ylabel(r'$\omega_e$ (rad/s)', fontsize=12)
ax2.set_ylabel(r'$T_e$ (Nm)', fontsize=12)
ax2.set_xlabel('Time (ms)', fontsize=12)

ax1.legend(loc='lower right', frameon=True, fontsize=10)
ax2.legend(loc='lower right', frameon=True, fontsize=10)

ax1.grid(True, linestyle=':', alpha=0.6)
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.set_xlim([0, 85]) 

# Annotations (a), (b)
ax1.text(0.95, 0.1, '(a)', transform=ax1.transAxes, fontsize=12, fontweight='bold', ha='right')
ax2.text(0.95, 0.1, '(b)', transform=ax2.transAxes, fontsize=12, fontweight='bold', ha='right')

plt.savefig(OUTPUT_FILE, dpi=300)
print(f"Figure saved to {OUTPUT_FILE}")
