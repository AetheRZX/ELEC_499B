import scipy.io
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

# --- CONFIGURATION ---
DATA_FOLDER = Path('mat_files_v2')
OUTPUT_FOLDER = Path('figures')

# Time settings
STEP_TIME_S = 1.0       # Absolute time of step
PLOT_WINDOW_MS = 40     # Duration to show after step
PRE_STEP_MS = 5         # Duration to show before step

# Define styles
STYLES = {
    # Changed labels to omega_r hat
    'LUT':    {'label': r'LUT $\hat{\omega}_r$',    'color': '#f1c40f', 'linestyle': '-', 'linewidth': 2},
    '3_step': {'label': r'3-step $\hat{\omega}_r$', 'color': '#2980b9', 'linestyle': '-', 'linewidth': 1.5},
    '6_step': {'label': r'6-step $\hat{\omega}_r$', 'color': '#e74c3c', 'linestyle': '-', 'linewidth': 1.5},
    
    # Changed Actual Ref to SOLID line
    'Ref':    {'label': r'Actual $\omega_r$',       'color': 'black',   'linestyle': '-', 'linewidth': 2, 'alpha': 0.6}
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
    Generates synthetic time vector if lengths mismatch.
    """
    len_t = len(ref_time)
    len_d = len(data_signal)
    if len_t == len_d:
        return ref_time
    return np.linspace(ref_time[0], ref_time[-1], len_d)

def plot_estimation_comparison(mtpa_state):
    print(f"\nProcessing Estimation Plot for MTPA_{mtpa_state}...")
    
    # 1. Load Baseline (Actual Speed from LUT scenario)
    baseline_data = load_mat_data('LUT', mtpa_state)
    if baseline_data is None:
        print("Error: Could not load LUT data for baseline.")
        return

    # Extract Baseline Data
    raw_time_base = baseline_data['time']
    omega_r_actual = baseline_data['omega_r'] # The "True" speed
    
    # Calculate timing constants
    abs_step_ms = STEP_TIME_S * 1000
    abs_start_ms = abs_step_ms - PRE_STEP_MS
    
    # Create Figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # --- PLOT 1: Baseline (Actual Speed) ---
    t_base_abs = get_aligned_time(raw_time_base, omega_r_actual) * 1000
    t_base_norm = t_base_abs - abs_start_ms
    
    st_ref = STYLES['Ref']
    ax.plot(t_base_norm, omega_r_actual, 
            label=st_ref['label'], color=st_ref['color'], 
            ls=st_ref['linestyle'], lw=st_ref['linewidth'], alpha=st_ref['alpha'])

    # --- PLOT 2,3,4: Estimated Speeds (omega_sw) ---
    has_data = False
    for strategy in PLOT_ORDER:
        data = load_mat_data(strategy, mtpa_state)
        if data is None: continue
        has_data = True
        
        raw_time = data['time']
        # Note: omega_sw is the ESTIMATED speed
        omega_est = data['omega_sw'] 
        
        # Align Time
        t_abs = get_aligned_time(raw_time, omega_est) * 1000
        t_norm = t_abs - abs_start_ms
        
        # Style
        st = STYLES.get(strategy)
        ax.plot(t_norm, omega_est, 
                label=st['label'], color=st['color'], 
                ls=st['linestyle'], lw=st['linewidth'])

    if not has_data:
        print("No estimation data found.")
        plt.close(fig)
        return

    # --- Formatting ---
    ax.set_ylabel(r'$\omega$ (rad/s)', fontsize=14)
    ax.set_xlabel('Time (ms)', fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Vertical Line at Step (happens at PRE_STEP_MS in normalized time)
    # Kept as dashed gray to contrast with the solid black line
    ax.axvline(x=PRE_STEP_MS, color='gray', linestyle='--', linewidth=1.5, alpha=0.8)
    
    # Legend
    ax.legend(loc='lower right', framealpha=1, edgecolor='k', fancybox=False, fontsize=11)
    
    # Limits
    # Increased upper limit to 1200 to avoid cutting off overshoot
    ax.set_ylim(500, 1150)
    ax.set_xlim(0, PRE_STEP_MS + PLOT_WINDOW_MS)
    
    # Save
    if not OUTPUT_FOLDER.exists():
        OUTPUT_FOLDER.mkdir(parents=True)
        
    out_name = OUTPUT_FOLDER / f'Speed_Estimation_MTPA_{mtpa_state}.png'
    plt.savefig(out_name, dpi=300, bbox_inches='tight')
    print(f"Saved {out_name}")
    plt.show()

if __name__ == "__main__":
    if not DATA_FOLDER.exists():
        print(f"Error: Folder '{DATA_FOLDER}' not found.")
    else:
        plot_estimation_comparison('off')
        plot_estimation_comparison('on')