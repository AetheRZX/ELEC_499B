import scipy.io
import matplotlib.pyplot as plt
import numpy as np
import os

# Configuration
DATA_FILE = os.path.join('mat_files', 'transient_run_lut1.mat')
OUTPUT_DIR = 'figures'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'current_transient_paper.png')
OFFSET_TIME = 0.5 # Filter activates here
MTPA_DELAY = 0.05 # MTPA activates 0.05s later (0.55s)

def plot_transient():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found.")
        return

    mat = scipy.io.loadmat(DATA_FILE)
    
    # helper
    def get_arr(keys):
        for k in keys:
            if k in mat: return mat[k].flatten()
        return None

    t = get_arr(['time'])
    i_a = get_arr(['i_a', 'i_as'])
    i_ds = get_arr(['i_ds'])
    i_ds_avg = get_arr(['i_ds_avg'])

    if t is None or i_a is None or i_ds is None or i_ds_avg is None:
        print("Missing signals.")
        return

    # Fix Length Mismatch
    # Find min length
    min_len = min(len(t), len(i_a), len(i_ds), len(i_ds_avg))
    print(f"Adjusting lengths to {min_len} (t={len(t)}, ia={len(i_a)}, ids={len(i_ds)})")
    
    t = t[:min_len]
    i_a = i_a[:min_len]
    i_ds = i_ds[:min_len]
    i_ds_avg = i_ds_avg[:min_len]

    # Normalize Time
    t_norm = t - OFFSET_TIME
    
    # Crop to interesting region
    t_min = -0.04
    t_max = 0.09 
    
    mask = (t_norm >= t_min) & (t_norm <= t_max)
    t_plot = t_norm[mask]
    ia_plot = i_a[mask]
    ids_plot = i_ds[mask]
    ids_avg_plot = i_ds_avg[mask]
    
    # Plotting
    fig, ax = plt.subplots(figsize=(10, 3), constrained_layout=True)
    
    ax.plot(t_plot, ia_plot, color='blue', linewidth=1.5, label='$i_{as}$')
    ax.plot(t_plot, ids_plot, color='red', linewidth=1.5, label='$i_{ds}$')
    ax.plot(t_plot, ids_avg_plot, color='black', linewidth=2.0, label='$\overline{i}_{ds}$')
    
    # Vertical Lines for transitions
    # 1. Filter Check (t=0)
    ax.axvline(0, color='k', linestyle='-.', linewidth=1.5)
    
    # 2. MTPA Check (t=0.05)
    ax.axvline(MTPA_DELAY, color='k', linestyle='-.', linewidth=1.5)
    
    # Annotations
    y_lbl = max(ia_plot) * 0.9 if len(ia_plot) > 0 else 10
    
    ax.text(t_min/2, y_lbl, 'Uncompensated', ha='center', fontsize=12, fontweight='bold', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    ax.text(MTPA_DELAY/2, y_lbl, 'Filter Only', ha='center', fontsize=12, fontweight='bold', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    ax.text(MTPA_DELAY + (t_max-MTPA_DELAY)/2, y_lbl, 'Filter + MTPA', ha='center', fontsize=12, fontweight='bold', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
    ax.set_ylabel('Current (A)', fontsize=12)
    ax.set_xlabel('Time (s) [Relative to Filter Activation]', fontsize=12)
    ax.set_xlim(t_min, t_max)
    
    ax.legend(loc='lower right', ncol=3)
    ax.grid(True, linestyle=':', alpha=0.6)

    output_path = OUTPUT_FILE
    plt.savefig(output_path, dpi=300)
    print(f"Saved plot to {output_path}")
    
if __name__ == "__main__":
    plot_transient()
