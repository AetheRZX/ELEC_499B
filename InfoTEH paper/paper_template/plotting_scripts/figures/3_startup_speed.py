import numpy as np
import scipy.io
import matplotlib.pyplot as plt
import os

# --- Configuration ---
DATA_DIR = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files"
OUTPUT_FILE = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\figures\3_startup_speed.png"

# Files for Speed Comparison
FILES = [
    {'name': '3_step_from_startup.mat',  'label': '3-Step Filter',   'color': '#77AC30', 'style': '-'}, 
    {'name': '6_step_from_startup.mat',  'label': '6-Step Filter',   'color': '#0072BD', 'style': '-'}, 
    {'name': 'LUT_from_startup.mat',     'label': 'Proposed LUT',    'color': '#D95319', 'style': '-'}, 
    {'name': 'no_misalignment_MTPA.mat', 'label': 'No Misalignment', 'color': 'k',       'style': '--'} 
]

POLE_PAIRS = 4

# --- Main Plotting ---
fig, ax1 = plt.subplots(1, 1, figsize=(7, 5), constrained_layout=True)

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
ax1.set_xlabel('Time (ms)', fontsize=12)
ax1.legend(loc='lower right', fontsize=10)
ax1.grid(True, linestyle=':', alpha=0.6)
# ax1.set_title('(a) Startup Speed Comparison', loc='left', fontsize=12, fontweight='bold')
# Removed (a) since it's a single plot now, or keep it if fitting into paper? 
# Usually single plot doesn't need (a). All good.

ax1.set_xlim([0, 200])

plt.savefig(OUTPUT_FILE, dpi=300)
print(f"Figure saved to {OUTPUT_FILE}")
