import scipy.io
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

# --- CONFIGURATION ---
DATA_FOLDER = Path('mat_files_v2')

# Time settings
STEP_TIME_S = 1.0       # The absolute time the step happens in simulation (seconds)
PLOT_WINDOW_MS = 40     # How many ms to show after the step
PRE_STEP_MS = 5         # How many ms to show before the step (start of the plot)

# Define styles
STYLES = {
    'LUT':    {'label': 'LUT Correction',    'color': '#f1c40f', 'linestyle': '-', 'linewidth': 2},
    '3_step': {'label': '3-step averaging',  'color': '#2980b9', 'linestyle': '-', 'linewidth': 1.5},
    '6_step': {'label': '6-step averaging',  'color': '#e74c3c', 'linestyle': '-', 'linewidth': 1.5},
}
PLOT_ORDER = ['LUT', '3_step', '6_step']

def load_mat_data(strategy, mtpa_state):
    filename = f"{strategy}_speed_transient_MTPA_{mtpa_state}.mat"
    file_path = DATA_FOLDER / filename
    
    if not file_path.exists():
        print(f"Skipping: {filename} (not found)")
        return None

    try:
        return scipy.io.loadmat(str(file_path), squeeze_me=True)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def get_aligned_time(ref_time, data_signal):
    """
    Fixes mismatched dimensions by generating a synthetic time vector
    if the data length doesn't match the reference time length.
    """
    len_t = len(ref_time)
    len_d = len(data_signal)

    if len_t == len_d:
        return ref_time
    
    return np.linspace(ref_time[0], ref_time[-1], len_d)

def plot_scenario(mtpa_state):
    print(f"\nProcessing MTPA_{mtpa_state}...")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    plt.subplots_adjust(hspace=0.08)
    
    has_data = False
    
    # Calculate absolute timings in ms
    abs_step_ms = STEP_TIME_S * 1000
    abs_start_ms = abs_step_ms - PRE_STEP_MS
    
    # Calculate Plot Limits (Normalized)
    # Start = 0
    # End = Pre_step + Window
    x_lim_start = 0
    x_lim_end = PRE_STEP_MS + PLOT_WINDOW_MS
    
    for strategy in PLOT_ORDER:
        data = load_mat_data(strategy, mtpa_state)
        if data is None: continue
        
        has_data = True
        
        # Extract Raw Data
        raw_time = data['time']       
        speed = data['omega_r']
        torque = data['T_e']
        
        # --- Generate aligned time vectors (ms) ---
        t_speed_abs = get_aligned_time(raw_time, speed) * 1000
        t_torque_abs = get_aligned_time(raw_time, torque) * 1000
        
        # --- NORMALIZE TIME ---
        # Shift time so that 'abs_start_ms' becomes 0
        t_speed_norm = t_speed_abs - abs_start_ms
        t_torque_norm = t_torque_abs - abs_start_ms
        
        # Style
        st = STYLES.get(strategy, {'label': strategy, 'color': 'k', 'ls': '-'})
        
        # Plot Speed
        ax1.plot(t_speed_norm, speed, 
                 label=st['label'], color=st['color'], 
                 ls=st.get('linestyle', '-'), lw=st.get('linewidth', 1.5))
        
        # Plot Torque
        ax2.plot(t_torque_norm, torque, 
                 label=st['label'], color=st['color'], 
                 ls=st.get('linestyle', '-'), lw=st.get('linewidth', 1.5))

    if not has_data:
        print(f"No data found for MTPA_{mtpa_state}, skipping plot.")
        plt.close(fig)
        return

    # --- Formatting Speed ---
    ax1.set_ylabel(r'$\omega_e$ (rad/s)', fontsize=12)
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    # Vertical Line: Now happens at PRE_STEP_MS (e.g., 5ms) because 0 is the start of window
    ax1.axvline(x=PRE_STEP_MS, color='gray', linestyle='--', linewidth=1.5, alpha=0.8)
    
    ax1.legend(loc='lower right', framealpha=1, edgecolor='k', fancybox=False)
    ax1.set_ylim(500, 1000)

    # --- Formatting Torque ---
    ax2.set_ylabel(r'$T_e$ (Nm)', fontsize=12)
    ax2.set_xlabel('Time (ms)', fontsize=12)
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    # Vertical Line
    ax2.axvline(x=PRE_STEP_MS, color='gray', linestyle='--', linewidth=1.5, alpha=0.8)

    ax2.set_ylim(-1.5, 3)

    # --- Zoom X-Axis (Normalized) ---
    ax2.set_xlim(x_lim_start, x_lim_end)

    # Save
    out_name = f'Plot_MTPA_{mtpa_state}.png'
    plt.savefig(out_name, dpi=300, bbox_inches='tight')
    print(f"Saved {out_name}")
    plt.show()

if __name__ == "__main__":
    if not DATA_FOLDER.exists():
        print(f"Error: Folder '{DATA_FOLDER}' not found.")
    else:
        plot_scenario('off')
        plot_scenario('on')