
import numpy as np
import matplotlib.pyplot as plt
import scipy.io
import os

# --- Configuration ---
# Adjust paths relative to this script location (inside python_scripts)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
OUTPUT_DIR = os.path.join(PARENT_DIR, 'figures') # Save figures in parent/figures as before? Or python_scripts/figures? 
# User said "figures" before. Let's keep it in the main plotting_scripts/figures to be consistent with previous runs, or maybe inside python_scripts/figures.
# "make python scripts in the python_scripts folder" - usually implies running from there.
# Let's put figures in `python_scripts/figures` to keep it self-contained, or `../figures`.
# Given the user wants to clean up, maybe keeping output in `../figures` is cleaner for the main repo, or `figures` inside `python_scripts`.
# I'll stick to `../figures` to avoid moving existing figures, or just `figures` relative to script.
# Let's use `figures` relative to the script for now to keep things tidy in the new folder structure? 
# User didn't specify figure location, just script location. I will use `../figures` to maintain consistency with existing figures.
OUTPUT_DIR = os.path.join(PARENT_DIR, 'figures')

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

MAT_FILES_V2 = os.path.join(PARENT_DIR, 'mat_files_v2')
MAT_FILES_V1 = os.path.join(PARENT_DIR, 'mat_files')

# Data Definitions
# Standard Set
STD_FILES = {
    'LUT': os.path.join(MAT_FILES_V2, 'LUT_transient_voltage.mat'),
    '3-Step': os.path.join(MAT_FILES_V2, '3_step_transient_voltage.mat'),
    '6-Step': os.path.join(MAT_FILES_V2, '6_step_transient_voltage.mat')
}

MTPA_FILES = {
    'LUT (MTPA)': os.path.join(MAT_FILES_V2, 'LUT_speed_transient_with_MTPA.mat'),
    '3-Step (MTPA)': os.path.join(MAT_FILES_V2, '3_step_speed_transient_with_MTPA.mat'),
    '6-Step (MTPA)': os.path.join(MAT_FILES_V2, '6_step_speed_transient_with_MTPA.mat')
}

# Torque Step Files (if different)
# The user wants "Speed and Torque" for "Transient Voltage" AND "Torque Step".
# Let's define Torque Step sets too.
STD_TORQUE_FILES = {
    'LUT': os.path.join(MAT_FILES_V1, 'LUT_torque_step.mat'),
    '3-Step': os.path.join(MAT_FILES_V1, '3_step_torque_step.mat'),
    '6-Step': os.path.join(MAT_FILES_V1, '6_step_torque_step.mat')
}

MTPA_TORQUE_FILES = {
    'LUT (MTPA)': os.path.join(MAT_FILES_V2, 'LUT_torque_transient_with_MTPA.mat'),
    '3-Step (MTPA)': os.path.join(MAT_FILES_V2, '3_step_torque_transient_with_MTPA.mat'),
    '6-Step (MTPA)': os.path.join(MAT_FILES_V2, '6_step_torque_transient_with_MTPA.mat')
}

# Colors matching the reference image approximately
# LUT: Yellow/Orange
# 3-step: Blue
# 6-step: Red
COLORS_MAP = {
    'LUT': '#FFC107',         # Amber/Yellow
    'LUT (MTPA)': '#FFC107',
    '3-Step': '#1f77b4',      # Standard Blue
    '3-Step (MTPA)': '#1f77b4',
    '6-Step': '#d62728',      # Standard Red
    '6-Step (MTPA)': '#d62728'
}

LINE_STYLES = {
    'LUT': '-',
    '3-Step': '-',
    '6-Step': '-',
    'LUT (MTPA)': '-',
    '3-Step (MTPA)': '-',
    '6-Step (MTPA)': '-'
}

def load_data(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return None
    try:
        mat = scipy.io.loadmat(path)
        data = {}
        data['time'] = mat['time'].flatten() if 'time' in mat else None
        
        # Length check helper
        n_t = len(data['time']) if data['time'] is not None else 0
        
        # Speed
        if 'rotor_speed' in mat:
            s = mat['rotor_speed'].flatten()
        elif 'omega_r' in mat:
            s = mat['omega_r'].flatten()
        else:
            s = None
        
        if s is not None and len(s) != n_t:
             # Simple truncation
             m = min(len(s), n_t)
             data['speed'] = s[:m]
             data['time'] = data['time'][:m]
             n_t = m 
        else:
            data['speed'] = s

        # Torque
        if 'T_e' in mat:
            t_val = mat['T_e'].flatten()
        else:
            t_val = None
            
        if t_val is not None and len(t_val) != n_t:
            m = min(len(t_val), n_t)
            data['torque'] = t_val[:m]
            # Update time/speed if torque is shorter (rare but possible)
            data['time'] = data['time'][:m]
            if data['speed'] is not None:
                data['speed'] = data['speed'][:m]
        elif t_val is None:
            # Try to calculate Torque: T_e = 1.5 * i_q * e_q / omega_r
            # Need i_a, i_b, theta_r, e_q, omega_r
            if all(k in mat for k in ['i_a', 'i_b', 'theta_r', 'e_q']):
                try:
                    i_a = mat['i_a'].flatten()[:n_t]
                    i_b = mat['i_b'].flatten()[:n_t]
                    theta_r = mat['theta_r'].flatten()[:n_t]
                    e_q = mat['e_q'].flatten()[:n_t]
                    
                    # Using omega_r for scaling is tricky near zero. Use separate check?
                    # Or simpler: T_e = 1.5 * i_q * (e_q / omega) ?
                    # If e_q ~ k * w, then e_q/w is constant (Flux).
                    # Let's rely on T = 1.5 * i_q * Flux.
                    # We can estimate Flux from e_q / speed where speed is high enough.
                    # Or just use T_e = 1.5 * i_q * e_q / speed.
                    
                    # 1. Clarke (Power invariant? Usually amplitude invariant for these controls)
                    # i_alpha = i_a
                    # i_beta = (i_a + 2*i_b) / sqrt(3)
                    i_alpha = i_a
                    i_beta = (i_a + 2*i_b) / np.sqrt(3)
                    
                    # 2. Park
                    # i_d = i_alpha * cos(theta) + i_beta * sin(theta)
                    # i_q = -i_alpha * sin(theta) + i_beta * cos(theta)
                    sin_t = np.sin(theta_r)
                    cos_t = np.cos(theta_r)
                    i_q = -i_alpha * sin_t + i_beta * cos_t
                    
                    if data['speed'] is not None:
                        w = data['speed']
                        # Avoid div by zero
                        mask = np.abs(w) > 1.0
                        te_calc = np.zeros_like(i_q)
                        te_calc[mask] = 1.5 * i_q[mask] * e_q[mask] / w[mask]
                        # Fill zeros? Or interpolate?
                        data['torque'] = te_calc
                        print(f"Calculated Torque for {path}")
                    else:
                        print("Cannot calculate torque: missing speed")
                        data['torque'] = None
                except Exception as ex:
                    print(f"Torque calc failed: {ex}")
                    data['torque'] = None
            else:
                 data['torque'] = None
        else:
            data['torque'] = t_val
            
        return data
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

def find_step_index(data, trigger_signal='speed', trigger_level=600, trigger_edge='rising'):
    """
    Returns the index where the signal crosses the threshold.
    """
    if trigger_signal == 'speed':
        sig = data['speed']
    elif trigger_signal == 'torque':
        sig = data['torque']
    else:
        return None
        
    if sig is None:
        return None

    # Simple threshold crossing
    if trigger_edge == 'rising':
        # Find first index where sig > level
        # Start searching from e.g. 10% to avoid initial glitches if needed, but let's try 0.
        # But for 'rising', we want transition low->high.
        # mask = speed > level. Find diff.
        mask = sig > trigger_level
        # crossings = np.where(np.diff(mask.astype(int)) > 0)[0] + 1
        # Or just first value > level (assuming it starts lower)
        gt = np.where(sig > trigger_level)[0]
        if len(gt) > 0:
            return gt[0]
            
    elif trigger_edge == 'falling':
        lt = np.where(sig < trigger_level)[0]
        if len(lt) > 0:
            return lt[0]
            
    return None

def plot_stacked_response(file_map, title, filename_suffix, 
                          trigger_signal='speed', trigger_level=600, trigger_edge='rising',
                          x_window=[-0.005, 0.025], 
                          ylim_speed=None, ylim_torque=None):
    """
    Plots Speed (top) and Torque (bottom) stacked.
    Normalizes time such that the step is at t=0.
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10), sharex=True)
    
    # Fonts
    plt.rcParams.update({'font.size': 14, 'font.family': 'serif'})
    
    found_any = False
    
    for label, path in file_map.items():
        data = load_data(path)
        if data is None or data['time'] is None:
            continue
            
        # Find Step
        idx = find_step_index(data, trigger_signal, trigger_level, trigger_edge)
        
        if idx is not None:
             found_any = True
             t_zero = data['time'][idx]
             t_shifted = data['time'] - t_zero
             
             # Color/Style
             color = COLORS_MAP.get(label, 'k')
             ls = LINE_STYLES.get(label, '-')
             display_label = label.replace(" (MTPA)", "")
             
             if data['speed'] is not None:
                 ax1.plot(t_shifted, data['speed'], label=display_label, color=color, linestyle=ls, linewidth=2)
             if data['torque'] is not None:
                 ax2.plot(t_shifted, data['torque'], label=display_label, color=color, linestyle=ls, linewidth=2)
                 
        else:
             print(f"No step detected in {label} (Signal: {trigger_signal}, Level: {trigger_level})")

    if not found_any:
        print(f"No aligned data for {filename_suffix}")
        plt.close(fig)
        return

    # Styling
    ax1.set_ylabel(r'$\omega_e$ (rad/s)')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.axvline(x=0, color='gray', linestyle='--', linewidth=2, alpha=0.8) # Step at 0
    ax1.legend(loc='lower right', frameon=True, framealpha=1.0, edgecolor='black')
    
    if ylim_speed:
        ax1.set_ylim(ylim_speed)

    ax2.set_ylabel(r'$T_e$ (Nm)')
    ax2.set_xlabel('Time (s)')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.axvline(x=0, color='gray', linestyle='--', linewidth=2, alpha=0.8)
    
    if ylim_torque:
        ax2.set_ylim(ylim_torque)
    
    # Zoom Window
    ax1.set_xlim(x_window)
        
    ax1.set_title(title, pad=20)
    
    plt.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, f'stacked_{filename_suffix}.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved {save_path}")
    plt.close(fig)

# --- Execution ---

# 1. Voltage Step (Standard)
# Trigger: Speed rising past 600
print("Generating Voltage Step (Standard)...")
plot_stacked_response(STD_FILES, "Voltage Step Response (Standard)", "voltage_std", 
                      trigger_signal='speed', trigger_level=600, trigger_edge='rising',
                      x_window=[-0.005, 0.025], 
                      ylim_speed=[500, 950],
                      ylim_torque=[-1.5, 1.5])

# 2. Voltage Step (MTPA)
print("Generating Voltage Step (MTPA)...")
plot_stacked_response(MTPA_FILES, "Voltage Step Response (MTPA)", "voltage_mtpa", 
                      trigger_signal='speed', trigger_level=600, trigger_edge='rising',
                      x_window=[-0.005, 0.025], 
                      ylim_speed=[500, 950],
                      ylim_torque=[-1.5, 1.5])

# 3. Torque Step (Standard)
# Trigger: Torque rising past 0.5? Or Speed dropping?
# Let's try Torque > 0.5. (Torque step pushes torque up)
# If torque is missing and calculated potentially noisy, careful.
# But we fixed torque calc.
print("Generating Torque Step (Standard)...")
plot_stacked_response(STD_TORQUE_FILES, "Torque Step Response (Standard)", "torque_std", 
                      trigger_signal='torque', trigger_level=0.5, trigger_edge='rising',
                      x_window=[-0.005, 0.025],
                      ylim_torque=[-1.5, 1.5]) 

# 4. Torque Step (MTPA)
print("Generating Torque Step (MTPA)...")
plot_stacked_response(MTPA_TORQUE_FILES, "Torque Step Response (MTPA)", "torque_mtpa", 
                      trigger_signal='torque', trigger_level=0.5, trigger_edge='rising',
                      x_window=[-0.005, 0.025],
                      ylim_torque=[-1.5, 1.5])
