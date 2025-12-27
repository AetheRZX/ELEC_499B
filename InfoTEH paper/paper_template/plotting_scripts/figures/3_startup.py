import numpy as np
import scipy.io
import matplotlib.pyplot as plt
import os

# --- Configuration ---
DATA_DIR = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files"
OUTPUT_FILE = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\figures\3_startup.png"

# Files
FILES = [
    {'name': '3_step_from_startup.mat',  'label': '3-Step Filter',   'color': '#77AC30', 'style': '-'}, # Green
    {'name': '6_step_from_startup.mat',  'label': '6-Step Filter',   'color': '#0072BD', 'style': '-'}, # Blue
    {'name': 'LUT_from_startup.mat',     'label': 'Proposed LUT',    'color': '#D95319', 'style': '-'}, # Red/Orange
    {'name': 'no_misalignment_MTPA.mat', 'label': 'No Misalignment', 'color': 'k',       'style': '--'} # Black Dashed
]

# --- Main Plotting ---
fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)

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
            spd = data['omega_r'].flatten() * (60 / (2*np.pi * 4)) # Assume P=4
        else:
            print(f"Speed key not found in {f['name']}")
            continue
            
        mask = t <= 0.25
        ax.plot(t[mask]*1000, spd[mask], label=f['label'], color=f['color'], linestyle=f['style'], linewidth=1.5)
        
    except Exception as e:
        print(f"Error loading {f['name']}: {e}")

ax.set_xlabel('Time (ms)', fontsize=12)
ax.set_ylabel('Rotor Speed (RPM)', fontsize=12)
ax.set_xlim([0, 200]) # 0.2s
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(loc='lower right', frameon=True, fontsize=10)

plt.savefig(OUTPUT_FILE, dpi=300)
print(f"Figure saved to {OUTPUT_FILE}")
