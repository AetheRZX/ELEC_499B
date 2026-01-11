
import scipy.io
import numpy as np
import matplotlib.pyplot as plt
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
# Path to Standard LUT file
FILE_PATH = os.path.join(PARENT_DIR, 'mat_files_v2', 'LUT_transient_voltage.mat')

try:
    mat = scipy.io.loadmat(FILE_PATH)
    time = mat['time'].flatten()
    if 'rotor_speed' in mat:
        speed = mat['rotor_speed'].flatten()
    elif 'omega_r' in mat:
        speed = mat['omega_r'].flatten()
    else:
        print("No speed data found.")
        exit()
        
    # Standard speed jump is usually from ~530 to ~900?
    # Let's look for where it crosses 600.
    crossings = np.where(speed > 600)[0]
    if len(crossings) > 0:
        idx = crossings[0]
        step_time = time[idx]
        print(f"Speed crosses 600 rad/s at index {idx}, time {step_time:.4f} s.")
        
        # Plot around there to verify
        plt.figure()
        plt.plot(time, speed)
        plt.axvline(x=step_time, color='r')
        plt.xlim([step_time - 0.1, step_time + 0.1])
        plt.title(f"Detected Step at {step_time:.4f}s")
        save_path = os.path.join(BASE_DIR, 'debug_step_loc.png')
        plt.savefig(save_path)
        print(f"Saved debug plot to {save_path}")
    else:
        print("Speed does not cross 600 rad/s. Max speed:", np.max(speed))
        
except Exception as e:
    print(f"Error: {e}")
