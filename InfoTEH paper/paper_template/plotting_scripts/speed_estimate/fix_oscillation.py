
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from pathlib import Path

# ================= CONFIGURATION =================
FILE_M3 = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files\speed_estimation_test_M3.mat"
OUTPUT_DIR = Path(r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\speed_estimate")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# User-Provided M3 LUT (Degrees)
M3_LUT_RAD_USER = np.array([1.0500, 0.9454, 1.1459, 1.0499, 0.9453, 1.1459])
M3_LUT_DEG_USER = np.rad2deg(M3_LUT_RAD_USER)

def load_mat_data(filepath):
    try:
        data = sio.loadmat(filepath)
        return {
            'time': data['time'].flatten(),
            'omega_r': data['omega_r'].flatten(),
            'hardware_ISR': data['hardware_ISR'].flatten()
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

def find_rising_edges(signal):
    return np.where((signal[:-1] <= 0.5) & (signal[1:] > 0.5))[0] + 1

def compute_speed_lut(time, edge_indices, lut_angles_deg, shift=0):
    if len(edge_indices) < 2: return np.array([]), np.array([])
    
    est_speed = []
    est_time = []
    
    for i in range(1, len(edge_indices)):
        idx_curr = edge_indices[i]
        idx_prev = edge_indices[i-1]
        dt = time[idx_curr] - time[idx_prev]
        if dt < 1e-6: continue
        
        # Determine sector index
        lut_idx = (i - 1 + shift) % 6
        deg = lut_angles_deg[lut_idx]
        w = np.deg2rad(deg) / dt
        
        est_speed.append(w)
        est_time.append(time[idx_curr])
        
    return np.array(est_time), np.array(est_speed)

def compute_ideal_angles(time, edge_indices, real_speed, shift=0):
    # Calculate what the angle SHOULD be to match the average speed
    # Then group by sector index (0..5) and average them to get the Ideal LUT
    
    sector_angles = [[] for _ in range(6)]
    
    for i in range(1, len(edge_indices)):
        idx_curr = edge_indices[i]
        idx_prev = edge_indices[i-1]
        dt = time[idx_curr] - time[idx_prev]
        
        # Get true average speed in this interval
        w_avg = np.mean(real_speed[idx_prev:idx_curr+1])
        
        # Ideal Angle = w * dt
        angle_deg = np.rad2deg(w_avg * dt)
        
        lut_idx = (i - 1 + shift) % 6
        sector_angles[lut_idx].append(angle_deg)
        
    ideal_lut = np.array([np.mean(vals) for vals in sector_angles])
    return ideal_lut

def main():
    print("Loading M3 Data...")
    data = load_mat_data(FILE_M3)
    if data is None: return

    edges = find_rising_edges(data['hardware_ISR'])
    
    # 1. Determine Best Shift for User LUT
    # (We iterate to ensure we are comparing apples to apples)
    best_shift = 0
    min_err = float('inf')
    
    # We'll also calculate Ideal LUT for the BEST shift
    # Because Ideal LUT depends on which physical sector maps to index 0
    
    print("Finding best shift for User LUT...")
    for s in range(6):
        t, w = compute_speed_lut(data['time'], edges, M3_LUT_DEG_USER, shift=s)
        # Compare to real speed
        w_real = np.interp(t, data['time'], data['omega_r'])
        err = np.mean((w - w_real)**2)
        if err < min_err:
            min_err = err
            best_shift = s
    
    print(f"Best Shift for User LUT: {best_shift}")
    
    # 2. Calculate Ideal LUT for this same shift
    # (So that index 0 of Ideal corresponds to index 0 of User LUT)
    ideal_lut_deg = compute_ideal_angles(data['time'], edges, data['omega_r'], shift=best_shift)
    
    with open(OUTPUT_DIR / "ideal_lut.txt", "w") as f:
        f.write("Index | User Config | Calculated Ideal | Diff\n")
        f.write("---------------------------------------------\n")
        for i in range(6):
            f.write(f"  {i}   |   {M3_LUT_DEG_USER[i]:.4f}    |     {ideal_lut_deg[i]:.4f}     | {ideal_lut_deg[i]-M3_LUT_DEG_USER[i]:.4f}\n")
    print(f"Values saved to {OUTPUT_DIR / 'ideal_lut.txt'}")

    # 3. Generate Comparison Plot
    t_user, w_user = compute_speed_lut(data['time'], edges, M3_LUT_DEG_USER, shift=best_shift)
    t_ideal, w_ideal = compute_speed_lut(data['time'], edges, ideal_lut_deg, shift=best_shift)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    
    # Zoom in on a steady section to show oscillation clearly
    # Find a section where speed is roughly constant
    mid_idx = len(t_user) // 2
    zoom_range = slice(mid_idx, mid_idx + 60) # Show ~10 mechanical revs
    
    # Plot 1: Speed Est (Full)
    ax1.plot(data['time'], data['omega_r'], 'k-', alpha=0.3, lw=3, label='Real Speed')
    ax1.step(t_user, w_user, where='post', color='r', alpha=0.6, label='User LUT (Config)')
    ax1.step(t_ideal, w_ideal, where='post', color='g', lw=2, label='Ideal LUT (Calculated)')
    ax1.set_title("Full Speed Profile")
    ax1.legend()
    
    # Plot 2: Zoomed Oscillation
    ax2.plot(data['time'], data['omega_r'], 'k-', alpha=0.3, lw=5, label='Real Speed')
    ax2.step(t_user, w_user, where='post', color='r', lw=1.5, label='User LUT')
    ax2.step(t_ideal, w_ideal, where='post', color='g', lw=2, linestyle='--', label='Ideal LUT')
    
    # Set Zoom Limits
    t_zoom_start = t_user[mid_idx]
    t_zoom_end = t_user[mid_idx+60]
    ax2.set_xlim(t_zoom_start, t_zoom_end)
    # Autoscale Y
    y_vals = w_user[zoom_range]
    ax2.set_ylim(np.min(y_vals)*0.95, np.max(y_vals)*1.05)
    
    ax2.set_title("Zoomed: Oscillation Detail")
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "oscillation_analysis_M3.png")
    print(f"Plot saved to {OUTPUT_DIR / 'oscillation_analysis_M3.png'}")

if __name__ == "__main__":
    main()
