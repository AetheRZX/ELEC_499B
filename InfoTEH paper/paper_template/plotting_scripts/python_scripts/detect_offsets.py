
import scipy.io
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
MAT_FILES_V2 = os.path.join(PARENT_DIR, 'mat_files_v2')

STD_FILES = {
    'LUT': os.path.join(MAT_FILES_V2, 'LUT_transient_voltage.mat'),
    '3-Step': os.path.join(MAT_FILES_V2, '3_step_transient_voltage.mat'),
    '6-Step': os.path.join(MAT_FILES_V2, '6_step_transient_voltage.mat')
}

THRESHOLD = 600.0

print("Detecting offsets (Crossing 600 rad/s)...")
for label, path in STD_FILES.items():
    if not os.path.exists(path):
        print(f"{label}: File not found")
        continue
    try:
        mat = scipy.io.loadmat(path)
        time = mat['time'].flatten()
        if 'rotor_speed' in mat:
            speed = mat['rotor_speed'].flatten()
        elif 'omega_r' in mat:
            speed = mat['omega_r'].flatten()
        else:
            print(f"{label}: No speed data")
            continue
            
        crossings = np.where(speed > THRESHOLD)[0]
        if len(crossings) > 0:
            idx = crossings[0]
            t_cross = time[idx]
            print(f"{label}: {t_cross:.5f}")
        else:
            print(f"{label}: No crossing found (Max: {np.max(speed):.1f})")
            
    except Exception as e:
        print(f"{label}: Error {e}")
