import scipy.io
import os
import numpy as np

DATA_FILE = os.path.join('mat_files', 'transient_run_lut1.mat')

def inspect_data():
    if not os.path.exists(DATA_FILE):
        print("LUT1 file not found.")
        return

    mat = scipy.io.loadmat(DATA_FILE)
    if 'time' in mat: t = mat['time'].flatten()
    elif 'i_a' in mat: t = np.linspace(0, 1, len(mat['i_a'])) # Fallback
    else: print("No time vector."); return
    
    print(f"Time Range: {t[0]:.4f} to {t[-1]:.4f} s")
    print(f"Signals: {mat.keys()}")
    
    if 'i_ds_avg' in mat:
        ids_avg = mat['i_ds_avg'].flatten()
        print(f"i_ds_avg stats: Min={min(ids_avg):.4f}, Max={max(ids_avg):.4f}")
        
    if 'i_ds' in mat:
        ids = mat['i_ds'].flatten()
        print(f"i_ds stats: Min={min(ids):.4f}, Max={max(ids):.4f}")

if __name__ == "__main__":
    inspect_data()
