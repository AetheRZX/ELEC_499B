
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from pathlib import Path
import os

# ================= CONFIGURATION =================
# Default LUT values (Degrees)
DEFAULT_LUT = np.array([55.998, 57.995, 65.991, 55.998, 57.994, 65.990])

# M2 LUT values (Radians -> Degrees)
# 0.9541, 1.1546, 1.0326, 0.9541, 1.1546, 1.0325
M2_LUT_RAD = np.array([0.9541, 1.1546, 1.0326, 0.9541, 1.1546, 1.0325])
M2_LUT_DEG = np.rad2deg(M2_LUT_RAD)

# M3 LUT values (Optimized Degrees)
# 65.9811, 48.4872, 65.4842, 65.9832, 48.4878, 65.4765
M3_LUT_DEG = np.array([65.9811, 48.4872, 65.4842, 65.9832, 48.4878, 65.4765])

OUTPUT_DIR = Path(r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\speed_estimate")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CASES = [
    {
        "name": "Default",
        "file": r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files\speed_estimation_test.mat",
        "lut_values": DEFAULT_LUT
    },
    {
        "name": "M2",
        "file": r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files\speed_estimation_test_M2.mat",
        "lut_values": M2_LUT_DEG
    },
    {
        "name": "M3",
        "file": r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files\speed_estimation_test_M3.mat",
        "lut_values": M3_LUT_DEG
    }
]

def load_mat_data(filepath):
    """Loads the .mat file."""
    path_obj = Path(filepath)
    if not path_obj.exists():
        print(f"Error: File '{path_obj}' not found.")
        return None
    try:
        data = sio.loadmat(str(path_obj))
        struct = {
            'time': data['time'].flatten(),
            'omega_r': data['omega_r'].flatten(), # Real Speed
            'hardware_ISR': data['hardware_ISR'].flatten(),
            'software_ISR': data['software_ISR'].flatten()
        }
        return struct
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def find_rising_edges(signal):
    """Finds indices where signal transitions from low to high."""
    return np.where((signal[:-1] <= 0.5) & (signal[1:] > 0.5))[0] + 1

def compute_speed_lut(time, edge_indices, lut_angles_deg, shift=0):
    """Calculates speed using LUT angles with a specific shift."""
    if len(edge_indices) < 2:
        return np.array([]), np.array([])
    
    est_speed = []
    est_time = []
    
    for i in range(1, len(edge_indices)):
        idx_curr = edge_indices[i]
        idx_prev = edge_indices[i-1]
        
        dt = time[idx_curr] - time[idx_prev]
        if dt < 1e-6: continue
        
        # Determine which sector this interval corresponds to
        # 'i' is the index of the edge. 
        # For N edges, there are N-1 intervals.
        # Interval 0 is between edge 0 and edge 1.
        lut_idx = (i - 1 + shift) % 6 
        
        deg = lut_angles_deg[lut_idx]
        d_theta = np.deg2rad(deg)
        
        w = d_theta / dt
        est_speed.append(w)
        est_time.append(time[idx_curr])
        
    return np.array(est_time), np.array(est_speed)

def compute_ideal_angles_from_data(time, edge_indices, real_speed_signal):
    """
    Reverse engineers the ideal LUT angles.
    Ideal Angle (deg) = Omega_r(avg) * dt * (180/pi)
    """
    if len(edge_indices) < 2:
        return np.zeros(6)

    angle_lists = [[] for _ in range(6)]
    
    for i in range(1, len(edge_indices)):
        idx_curr = edge_indices[i]
        idx_prev = edge_indices[i-1]
        
        dt = time[idx_curr] - time[idx_prev]
        if dt < 1e-6: continue
        
        # Get average real speed during this interval
        w_real = np.mean(real_speed_signal[idx_prev:idx_curr+1])
        
        ideal_deg = w_real * dt * (180.0 / np.pi)
        
        # We don't know the absolute sector alignment yet, so we store by modulo sequence
        # We will align this later or just report it as a sequence.
        seq_idx = (i - 1) % 6
        angle_lists[seq_idx].append(ideal_deg)
        
    # Average the lists to get the 6 ideal angles (in sequence order)
    ideal_lut = np.array([np.mean(l) if len(l) > 0 else 60.0 for l in angle_lists])
    return ideal_lut

def apply_low_pass(data, alpha=0.05):
    """Simple IIR Low Pass Filter."""
    if len(data) == 0: return data
    filtered = np.zeros_like(data)
    filtered[0] = data[0]
    for i in range(1, len(data)):
        filtered[i] = (alpha * data[i]) + ((1 - alpha) * filtered[i-1])
    return filtered

def process_case(case_info):
    name = case_info["name"]
    print(f"--- Processing {name} ---")
    data = load_mat_data(case_info["file"])
    if data is None: return

    # 1. Get Edges (Using Hardware ISR for accuracy)
    edges = find_rising_edges(data['hardware_ISR'])
    if len(edges) < 10:
        print(f"  Not enough edges found in {name}")
        return

    # 2. Calculate PI/3 Speed (Baseline) and Filter it
    t_fixed, w_fixed = compute_speed_lut(data['time'], edges, np.full(6, 60.0), shift=0)
    w_fixed_filt = apply_low_pass(w_fixed, alpha=0.05)
    
    # 3. Calculate Ideal Angles
    # Note: These are in sequence order found in file, we need to match them to the LUT.
    # Usually the physical Hall order is fixed, but the software index might shift.
    # We will assume the sequence in 'ideal_lut' corresponds to the sequence of intervals.
    ideal_lut_sequence = compute_ideal_angles_from_data(data['time'], edges, data['omega_r'])
    print(f"  Calculated Ideal Angles (seq): {np.round(ideal_lut_sequence, 2)}")

    # 4. Generate Plots
    fig = plt.figure(figsize=(15, 12))
    gs = fig.add_gridspec(3, 2)
    
    # -- Subplot 1: Estimators vs Real Speed (Big Plot) --
    ax_speed = fig.add_subplot(gs[0:2, :])
    ax_speed.plot(data['time'], data['omega_r'], 'k-', alpha=0.3, lw=3, label='Real Speed (Omega_r)')
    ax_speed.plot(t_fixed, w_fixed_filt, 'b--', lw=1.5, label='Filtered Pi/3 (Benchmark)')
    
    colors = plt.cm.viridis(np.linspace(0, 1, 6))
    
    # Use the specific LUT for this validation case
    current_lut = case_info["lut_values"]
    
    best_shift = 0
    min_error = float('inf')
    
    for shift in range(6):
        t_lut, w_lut = compute_speed_lut(data['time'], edges, current_lut, shift=shift)
        
        # Calculate consistency with Real Speed
        # Interpolate real speed to estimate time points
        w_real_interp = np.interp(t_lut, data['time'], data['omega_r'])
        error = np.mean((w_lut - w_real_interp)**2)
        
        label = f"LUT Shift {shift}"
        alpha = 0.5
        width = 1
        if error < min_error:
            min_error = error
            best_shift = shift
        
        ax_speed.step(t_lut, w_lut, where='post', color=colors[shift], alpha=alpha, lw=width, label=label)

    # Highlight best shift
    t_best, w_best = compute_speed_lut(data['time'], edges, current_lut, shift=best_shift)
    ax_speed.step(t_best, w_best, where='post', color='r', lw=2, linestyle=':', label=f'Best Shift ({best_shift})')

    ax_speed.set_title(f'{name}: Speed Estimation (All offsets)', fontsize=14)
    ax_speed.legend(loc='upper right', ncol=2)
    ax_speed.set_xlim(data['time'].min(), data['time'].max())

    # -- Subplot 2: Ideal vs Config LUT Comparison --
    ax_lut = fig.add_subplot(gs[2, :])

    # We need to align the Ideal Sequence to the Config LUT to see comparison
    # The 'best_shift' tells us how the Config LUT maps to the data sequence.
    # If shift=0 was best, then Index 0 of Data corresponds to Index 0 of LUT.
    # If shift=1 was best, then Interval 0 of Data used LUT[1]. 
    # So Ideal_Seq[0] corresponds to LUT[1].
    # We want to plot: x-axis = LUT Index (0..5).
    # y-axis = Angle.
    
    # Aligned Ideal LUT
    # If interval `i` matches `LUT[(i+shift)%6]`, then `Ideal[i]` matches `LUT[(i+shift)%6]`.
    # We want `Ideal_Aligned[k]` to compare with `LUT[k]`.
    # LUT[k] was used for Interval `i` where `(i+shift)%6 == k`.
    # So `Ideal_Aligned[k]` should be the average of ideal angles for intervals mapping to k.
    # But `ideal_lut_sequence` is already integrated by interval index modulo 6.
    # ideal_lut_sequence[0] is avg of intervals 0, 6, 12...
    # These intervals used LUT[(0+shift)%6].
    # So ideal_lut_sequence[0] compares to LUT[shift].
    # ideal_lut_sequence[1] compares to LUT[shift+1].
    
    # Let's verify:
    # We want to plot the Configuration LUT as the reference (Indices 0..5).
    # And map the calculated ideals to those indices.
    
    aligned_ideals = np.zeros(6)
    for i in range(6):
        target_lut_idx = (i + best_shift) % 6
        aligned_ideals[target_lut_idx] = ideal_lut_sequence[i]
    
    ax_lut.plot(range(6), current_lut, 'ro-', label='Configured LUT (Hardcoded/Default)')
    ax_lut.plot(range(6), aligned_ideals, 'bx--', label='Calculated Ideal Angles (from Data)')
    # Also plot the "Standard" 60 degrees
    ax_lut.axhline(60, color='gray', linestyle=':', label='Standard 60°')
        
    ax_lut.set_xticks(range(6))
    ax_lut.set_xlabel('LUT Index / Sector')
    ax_lut.set_ylabel('Angle (Degrees)')
    ax_lut.set_title(f'LUT Values Comparison (Aligned with Best Shift: {best_shift})')
    ax_lut.legend()
    ax_lut.grid(True)

    plt.tight_layout()
    save_path = OUTPUT_DIR / f"speed_estimate_{name}.png"
    plt.savefig(save_path)
    print(f"Saved plot to {save_path}")
    plt.close(fig)

def main():
    print("Starting Speed Estimation Analysis...")
    for case in CASES:
        process_case(case)
    print("Done.")

if __name__ == "__main__":
    main()
