import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from pathlib import Path

def load_mat_data(filepath):
    """Loads the .mat file using pathlib."""
    path_obj = Path(filepath)
    
    if not path_obj.exists():
        print(f"Error: File '{path_obj}' not found.")
        print(f"Absolute path checked: {path_obj.resolve()}")
        return None

    try:
        data = sio.loadmat(str(path_obj))
        # Flatten arrays to 1D
        struct = {
            'time': data['time'].flatten(),
            'omega_r': data['omega_r'].flatten(),
            'hardware_ISR': data['hardware_ISR'].flatten(),
            'software_ISR': data['software_ISR'].flatten()
        }
        return struct
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def find_rising_edges(signal):
    """
    Finds indices where signal transitions from low (<=0.5) to high (>0.5).
    """
    # signal[:-1] checks current state, signal[1:] checks next state
    rising_edges = (signal[:-1] <= 0.5) & (signal[1:] > 0.5)
    # Get indices (add 1 to get index of the 'high' value)
    return np.where(rising_edges)[0] + 1

def compute_speed(time, signal_name, signal, method='fixed', lut_angles_deg=None, lut_shift=0):
    """
    Calculates speed based on Rising Edge intervals (0 -> 1).
    """
    edge_indices = find_rising_edges(signal)
    
    if len(edge_indices) < 2:
        return np.array([]), np.array([])

    est_speed = []
    est_time = []
    
    for i in range(1, len(edge_indices)):
        idx_curr = edge_indices[i]
        idx_prev = edge_indices[i-1]
        
        dt = time[idx_curr] - time[idx_prev]
        
        if dt < 1e-6: continue

        if method == 'lut' and lut_angles_deg is not None:
            # Cycle through LUT based on edge count + shift
            lut_idx = (i + lut_shift) % len(lut_angles_deg)
            deg = lut_angles_deg[lut_idx]
            d_theta = np.deg2rad(deg)
        else:
            d_theta = np.pi / 3.0

        w = d_theta / dt
        est_speed.append(w)
        est_time.append(time[idx_curr])

    return np.array(est_time), np.array(est_speed)

def apply_low_pass(data, alpha=0.05):
    if len(data) == 0: return data
    filtered = np.zeros_like(data)
    filtered[0] = data[0]
    for i in range(1, len(data)):
        filtered[i] = (alpha * data[i]) + ((1 - alpha) * filtered[i-1])
    return filtered

def main():
    # ================= CONFIGURATION =================
    FILE_PATH = Path('mat_files') / 'speed_estimation_test.mat'
    
    # LUT Values (Degrees)
    LUT_ANGLES = np.array([55.998, 57.995, 65.991, 55.998, 57.994, 65.99])
    
    # Adjust these if the LUT estimation looks "jagged" or out of phase
    LUT_SHIFT_HW = 0  
    LUT_SHIFT_SW = 5

    ALPHA = 0.05
    # =================================================

    data = load_mat_data(FILE_PATH)
    if data is None: return

    # --- Calculations ---
    # 1. Standard
    t_hw, w_hw = compute_speed(data['time'], 'HW', data['hardware_ISR'], method='fixed')
    w_hw_filt = apply_low_pass(w_hw, alpha=ALPHA)
    t_sw, w_sw = compute_speed(data['time'], 'SW', data['software_ISR'], method='fixed')

    # 2. LUT
    t_lut_hw, w_lut_hw = compute_speed(data['time'], 'HW', data['hardware_ISR'], 
                                       method='lut', lut_angles_deg=LUT_ANGLES, lut_shift=LUT_SHIFT_HW)
    t_lut_sw, w_lut_sw = compute_speed(data['time'], 'SW', data['software_ISR'], 
                                       method='lut', lut_angles_deg=LUT_ANGLES, lut_shift=LUT_SHIFT_SW)

    # ================= FIGURE 1: OVERVIEW (Your original request) =================
    plt.style.use('bmh')
    fig1, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
    fig1.canvas.manager.set_window_title('Overview: All Estimators')

    # Plot 1: Standard
    axes[0].plot(data['time'], data['omega_r'], 'k-', alpha=0.3, lw=2, label='Real Speed')
    axes[0].step(t_hw, w_hw, where='post', label='HW (Fixed 60°)', lw=1.5)
    axes[0].step(t_sw, w_sw, where='post', label='SW (Fixed 60°)', linestyle='--', lw=1.5)
    axes[0].set_title('1. Standard Estimation (Fixed Pi/3)')
    axes[0].legend(loc='lower right')

    # Plot 2: Filtered
    axes[1].plot(data['time'], data['omega_r'], 'k-', alpha=0.3, lw=2, label='Real Speed')
    axes[1].step(t_hw, w_hw, where='post', label='HW Raw', alpha=0.5)
    axes[1].plot(t_hw, w_hw_filt, 'r-', lw=2, label=f'HW Filtered (alpha={ALPHA})')
    axes[1].set_title('2. Filtered Estimation')
    axes[1].legend(loc='lower right')

    # Plot 3: LUT Small
    axes[2].plot(data['time'], data['omega_r'], 'k-', alpha=0.3, lw=2, label='Real Speed')
    axes[2].step(t_lut_hw, w_lut_hw, where='post', label=f'HW LUT (Shift={LUT_SHIFT_HW})')
    axes[2].set_title('3. LUT Overview')
    axes[2].legend(loc='lower right')
    
    plt.tight_layout()

    # ================= FIGURE 2: LUT FOCUSED (Detailed View) =================
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    fig2.canvas.manager.set_window_title('Detailed View: LUT Estimation')

    # Real Speed (Thick, semi-transparent grey)
    ax2.plot(data['time'], data['omega_r'], color='black', alpha=0.3, linewidth=3, label='Real Motor Speed (omega_r)')

    # Hardware LUT (Solid Blue)
    ax2.step(t_lut_hw, w_lut_hw, where='post', color='#1f77b4', linewidth=1.5, 
             label=f'Hardware LUT (Shift={LUT_SHIFT_HW})')

    # Software LUT (Dashed Red - often overlaps HW, so using dashes helps visibility)
    ax2.step(t_lut_sw, w_lut_sw, where='post', color='#d62728', linestyle='--', linewidth=1.5, 
             label=f'Software LUT (Shift={LUT_SHIFT_SW})')

    ax2.set_title('LUT Speed Estimation vs Real Speed', fontsize=14)
    ax2.set_ylabel('Speed (rad/s)', fontsize=12)
    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.legend(loc='lower right', fontsize=10, frameon=True, fancybox=True, framealpha=0.9)
    ax2.grid(True, which='both', linestyle='--', alpha=0.7)

    print("Showing plots... (Check Figure 2 for the detailed LUT view)")
    plt.show()

if __name__ == "__main__":
    main()