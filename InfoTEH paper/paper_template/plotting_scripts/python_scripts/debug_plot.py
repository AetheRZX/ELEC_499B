
import numpy as np
import matplotlib.pyplot as plt
import scipy.io
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
OUTPUT_DIR = os.path.join(PARENT_DIR, 'figures')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

MAT_FILES_V2 = os.path.join(PARENT_DIR, 'mat_files_v2')

# Standard Voltage Files
STD_FILES = {
    'LUT': os.path.join(MAT_FILES_V2, 'LUT_transient_voltage.mat'),
    '3-Step': os.path.join(MAT_FILES_V2, '3_step_transient_voltage.mat'),
    '6-Step': os.path.join(MAT_FILES_V2, '6_step_transient_voltage.mat')
}

plt.figure(figsize=(10, 6))

for label, path in STD_FILES.items():
    try:
        if not os.path.exists(path):
            print(f"File not found: {path}")
            continue
            
        mat = scipy.io.loadmat(path)
        time = mat['time'].flatten()
        if 'rotor_speed' in mat:
            speed = mat['rotor_speed'].flatten()
        elif 'omega_r' in mat:
            speed = mat['omega_r'].flatten()
        else:
            speed = None
            
        if speed is not None:
             # Length Matching
             n = min(len(time), len(speed))
             plt.plot(time[:n], speed[:n], label=label, linewidth=1)
             
    except Exception as e:
        print(f"Error loading {label}: {e}")

plt.title("Debug: Full Scale Speed Response (Standard Voltage)")
plt.xlabel("Time (s)")
plt.ylabel("Speed (rad/s)")
plt.legend()
plt.grid(True)
save_path = os.path.join(OUTPUT_DIR, 'debug_full_scale_voltage.png')
plt.savefig(save_path, dpi=300)
print(f"Saved {save_path}")
