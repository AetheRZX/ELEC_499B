
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from pathlib import Path

# ================= CONFIGURATION =================
FILE_M3 = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files\speed_estimation_test_M3.mat"
OUTPUT_DIR = Path(r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\speed_estimate")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Optimized M3 LUT (Degrees) - we use the "Correct" LUT to isolate timing effects
M3_LUT_DEG = np.array([65.9811, 48.4872, 65.4842, 65.9832, 48.4878, 65.4765])

def load_mat_data(filepath):
    try:
        data = sio.loadmat(filepath)
        return {
            'time': data['time'].flatten(),
            'omega_r': data['omega_r'].flatten(),
            'hardware_ISR': data['hardware_ISR'].flatten(),
            'software_ISR': data['software_ISR'].flatten()
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

def find_rising_edges(signal):
    return np.where((signal[:-1] <= 0.5) & (signal[1:] > 0.5))[0] + 1

def compute_speed_mixed(time, hw_edges, sw_edges, lut_angles_deg, shift=0):
    # We need to couple HW[i-1] with SW[i]
    # First, ensure edges are aligned (SW comes after HW)
    
    # Simple alignment: Trim to min length
    n_edges = min(len(hw_edges), len(sw_edges))
    
    est_speed = []
    est_time = []
    
    for i in range(1, n_edges):
        # Index i is the "Current" event. 
        # We want interval ending at SW[i] and starting at HW[i-1]
        
        idx_sw_curr = sw_edges[i]
        idx_hw_prev = hw_edges[i-1]
        
        # Check causality: SW must be after HW
        # Also, HW[i-1] must be before SW[i]
        t_end = time[idx_sw_curr]
        t_start = time[idx_hw_prev]
        
        dt = t_end - t_start
        
        if dt < 1e-6: 
            # This shouldn't happen for a full sector, usually ~1ms+
            continue
            
        # Determine sector. 'i' is the completion count.
        lut_idx = (i - 1 + shift) % 6
        deg = lut_angles_deg[lut_idx]
        w = np.deg2rad(deg) / dt
        
        est_speed.append(w)
        est_time.append(t_end) # Plot at the time the estimate is available (SW interrupt)
        
    return np.array(est_time), np.array(est_speed)

def main():
    print("Loading Data...")
    data = load_mat_data(FILE_M3)
    if data is None: return

    hw_edges = find_rising_edges(data['hardware_ISR'])
    sw_edges = find_rising_edges(data['software_ISR'])
    
    print(f"Found {len(hw_edges)} HW edges and {len(sw_edges)} SW edges.")

    # Generate Plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot Real Speed
    ax.plot(data['time'], data['omega_r'], 'k-', alpha=0.3, lw=4, label='Real Speed')
    
    colors = plt.cm.viridis(np.linspace(0, 1, 6))
    
    # Loop over 6 offsets
    for s in range(6):
        t, w = compute_speed_mixed(data['time'], hw_edges, sw_edges, M3_LUT_DEG, shift=s)
        
        # Calculate Error for label
        if len(t) > 0:
            w_real = np.interp(t, data['time'], data['omega_r'])
            err = np.mean((w - w_real)**2)
            label = f"Shift {s} (MSE={err:.1f})"
        else:
            label = f"Shift {s}"
            
        ax.step(t, w, where='post', color=colors[s], alpha=0.7, lw=1.5, label=label)
        
    ax.set_title("Mixed Timing Speed Estimate: Angle / (SW[n] - HW[n-1])")
    ax.set_ylabel("Speed (rad/s)")
    ax.set_xlabel("Time (s)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    save_path = OUTPUT_DIR / "mixed_timing_analysis.png"
    plt.savefig(save_path)
    print(f"Plot saved to {save_path}")

if __name__ == "__main__":
    main()
