import numpy as np
import scipy.io
import matplotlib.pyplot as plt
import os
import scipy.signal

# --- Configuration ---
DATA_DIR = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files"
OUTPUT_FILE = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\figures\3_startup.png"

# Files for Speed Comparison
FILES = [
    {'name': '3_step_from_startup.mat',  'label': '3-Step Filter',   'color': '#77AC30', 'style': '-'}, 
    {'name': '6_step_from_startup.mat',  'label': '6-Step Filter',   'color': '#0072BD', 'style': '-'}, 
    {'name': 'LUT_from_startup.mat',     'label': 'Proposed LUT',    'color': '#D95319', 'style': '-'}, 
    {'name': 'no_misalignment_MTPA.mat', 'label': 'No Misalignment', 'color': 'k',       'style': '--'} 
]

POLE_PAIRS = 4

# --- Helper: Park Transform ---
def calc_id(i_a, i_b, i_c, theta_r):
    # i_d = 2/3 * (ia*cos(theta) + ib*cos(theta-2pi/3) + ic*cos(theta+2pi/3))
    cos_t = np.cos(theta_r)
    cos_tm = np.cos(theta_r - 2*np.pi/3)
    cos_tp = np.cos(theta_r + 2*np.pi/3)
    
    id_val = (2/3) * (i_a*cos_t + i_b*cos_tm + i_c*cos_tp)
    return id_val

# --- Main Plotting ---
fig, ax_arr = plt.subplots(3, 1, figsize=(8, 10), constrained_layout=True, sharex=True)
ax1, ax2, ax3 = ax_arr

# 1. Comparison of Speed (Ax1)
print("Plotting Speed Comparison...")
for f in FILES:
    path = os.path.join(DATA_DIR, f['name'])
    if not os.path.exists(path):
        print(f"File not found: {path}")
        continue
        
    try:
        data = scipy.io.loadmat(path)
        t = data['time'].flatten()
        
        if 'rotor_speed' in data:
            spd = data['rotor_speed'].flatten()
        elif 'omega_r' in data:
            spd = data['omega_r'].flatten() * (60 / (2*np.pi * POLE_PAIRS))
        else:
            continue
            
        mask = t <= 0.2
        ax1.plot(t[mask]*1000, spd[mask], label=f['label'], color=f['color'], linestyle=f['style'], linewidth=1.5)
        
    except Exception as e:
        print(f"Error loading {f['name']}: {e}")

ax1.set_ylabel('Speed (RPM)', fontsize=12)
ax1.legend(loc='lower right', fontsize=10)
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.set_title('(a) Startup Speed Comparison', loc='left', fontsize=12, fontweight='bold')


# 2. LUT Case currents (Ax2 & Ax3)
print("Plotting LUT Currents...")
lut_path = os.path.join(DATA_DIR, 'LUT_from_startup.mat')
if os.path.exists(lut_path):
    data = scipy.io.loadmat(lut_path)
    t = data['time'].flatten()
    mask = t <= 0.2
    
    # Extract
    t_plot = t[mask]*1000
    ia = data['i_a'].flatten()[mask]
    ib = data['i_b'].flatten()[mask]
    ic = data['i_c'].flatten()[mask]
    theta = data['theta_r'].flatten()[mask]
    
    # Ax2: Phase Currents
    ax2.plot(t_plot, ia, label=r'$i_a$', color='#0072BD', linewidth=1.0)
    ax2.plot(t_plot, ib, label=r'$i_b$', color='#D95319', linewidth=1.0)
    ax2.plot(t_plot, ic, label=r'$i_c$', color='#EDB120', linewidth=1.0)
    
    ax2.set_ylabel('Phase Currents (A)', fontsize=12)
    ax2.legend(loc='upper right', fontsize=10, ncol=3)
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.set_title('(b) LUT Phase Currents', loc='left', fontsize=12, fontweight='bold')
    
    # Ax3: D-axis Current
    id_raw = calc_id(ia, ib, ic, theta)
    
    # Filter for Avg
    try:
        dt = np.median(np.diff(t))
        if dt <= 0: raise ValueError("dt <= 0")
        fs = 1/dt
        
        fc = 50 
        if fc >= fs/2: fc = fs/2 - 1
            
        sos = scipy.signal.butter(2, fc, 'low', fs=fs, output='sos')
        id_avg = scipy.signal.sosfiltfilt(sos, id_raw)
    except Exception as e:
        print(f"Filter failed ({e}), using rolling mean")
        window = int(0.01 / dt) # 10ms
        if window < 1: window = 1
        id_avg = np.convolve(id_raw, np.ones(window)/window, mode='same')
    
    ax3.plot(t_plot, id_raw, label=r'$i_d$', color='#D95319', alpha=0.4, linewidth=0.8)
    ax3.plot(t_plot, id_avg, label=r'$\bar{i}_d$', color='k', linewidth=1.5, linestyle='--')
    
    ax3.set_ylabel(r'$d$-axis Current (A)', fontsize=12)
    ax3.set_xlabel('Time (ms)', fontsize=12)
    ax3.legend(loc='upper right', fontsize=10)
    ax3.grid(True, linestyle=':', alpha=0.6)
    ax3.set_title('(c) LUT d-axis Current', loc='left', fontsize=12, fontweight='bold')
    
ax3.set_xlim([0, 200])

plt.savefig(OUTPUT_FILE, dpi=300)
print(f"Figure saved to {OUTPUT_FILE}")
