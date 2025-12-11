import scipy.io
import numpy as np
import os

def analyze(tag):
    fpath = os.path.join('mat_files', f'torque_run_{tag}.mat')
    if not os.path.exists(fpath):
        print(f"{tag}: File not found")
        return

    mat = scipy.io.loadmat(fpath)
    t = mat['time'].flatten()
    ia = mat['i_a'].flatten()
    
    # Calculate Frequency based on zero crossings
    # Remove DC offset
    ia_ac = ia - np.mean(ia)
    hz_crossings = np.where(np.diff(np.sign(ia_ac)))[0]
    
    if len(hz_crossings) > 1:
        # Distance between crossings
        diffs = np.diff(t[hz_crossings])
        avg_half_period = np.mean(diffs)
        period = 2 * avg_half_period
        freq = 1 / period
        print(f"[{tag}] Time Range: {t[0]:.4f} to {t[-1]:.4f} s")
        print(f"[{tag}] Est. Frequency: {freq:.2f} Hz")
        print(f"[{tag}] Num Cycles in 4ms: {freq * 0.004:.2f}")
    else:
        print(f"[{tag}] Not enough zero crossings to estimate frequency.")

analyze('uncomp')
analyze('mtpa')
