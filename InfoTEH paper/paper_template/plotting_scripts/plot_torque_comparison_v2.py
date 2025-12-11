import scipy.io
import matplotlib.pyplot as plt
import numpy as np
import os

# Configuration
DATA_DIR = 'mat_files'
OUTPUT_DIR = 'figures'
os.makedirs(OUTPUT_DIR, exist_ok=True)

FILE_UNCOMP = os.path.join(DATA_DIR, 'torque_run_uncomp.mat')
FILE_LUT    = os.path.join(DATA_DIR, 'torque_run_lut.mat')
FILE_MTPA   = os.path.join(DATA_DIR, 'torque_run_mtpa.mat')

C_IA = '#005A9C' 
C_TE = '#C70039' 

import scipy.signal
def filter_signal(sig, fs, cutoff=1000, order=2):
    sos = scipy.signal.butter(order, cutoff, btype='low', fs=fs, output='sos')
    return scipy.signal.sosfiltfilt(sos, sig) 

def load_data(fpath):
    if not os.path.exists(fpath): 
        print(f"Warning: {fpath} not found.")
        return None
    mat = scipy.io.loadmat(fpath)
    t = mat['time'].flatten()
    ia = mat['i_a'].flatten()
    te = mat['T_e'].flatten()

    L = min(len(t), len(ia), len(te))
    t, ia, te = t[:L], ia[:L], te[:L]
    return t, ia, te

def calc_ratio_metric(t, te, ia, start_time=None):
    if start_time is not None:
        mask = t >= start_time
        t, te, ia = t[mask], te[mask], ia[mask]
    
    avg_te = np.mean(te)
    rms_ia = np.sqrt(np.mean(ia**2))
    ratio = avg_te / rms_ia if rms_ia > 1e-6 else 0
    return ratio

def plot_torque_comparison():
    # Load 4 Files
    d_uncomp = load_data(FILE_UNCOMP)
    file_filter = os.path.join(DATA_DIR, 'torque_run_filter.mat')
    d_filter = load_data(file_filter)
    d_lut    = load_data(FILE_LUT)
    d_mtpa   = load_data(FILE_MTPA)

    if not (d_uncomp and d_filter and d_lut and d_mtpa):
        print("Missing data files. Ensure you have run save_torque_runs for: uncomp, filter, lut, mtpa.")
        return

    # Metrics
    def get_steady_ratio(d):
        t = d[0]
        # Use last 30% of data to ensure steady state
        t_start = t[0] + (t[-1]-t[0])*0.7
        return calc_ratio_metric(d[0], d[2], d[1], start_time=t_start)

    r_uncomp = get_steady_ratio(d_uncomp)
    r_filter = get_steady_ratio(d_filter)
    r_lut    = get_steady_ratio(d_lut)
    r_mtpa   = get_steady_ratio(d_mtpa)

    # Plotting: Single Bar Chart
    fig, ax = plt.subplots(1, 1, figsize=(8, 5), constrained_layout=True)

    labels = ['Uncompensated', 'Filter Only', 'LUT Only', 'LUT + MTPA']
    vals = [r_uncomp, r_filter, r_lut, r_mtpa]
    colors = ['#0072BD', '#77AC30', '#EDB120', '#D95319'] # Blue, Green, Yellow, Red
    
    x = np.arange(len(labels))
    width = 0.6
    
    rects = ax.bar(x, vals, width, color=colors, alpha=0.85, edgecolor='k')
    
    ax.set_ylabel(r'Torque Constant $K_t$ (N$\cdot$m/A rms)', fontsize=12)
    ax.set_title(r'Torque Generation Efficiency ($\bar{T}_e / I_{rms}$)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11, fontweight='bold')
    ax.set_ylim(0, max(vals)*1.2)
    ax.grid(axis='y', ls='--', alpha=0.6)
    
    # Value Labels
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.4f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 5), textcoords="offset points",
                    ha='center', va='bottom', fontsize=12, fontweight='bold')

    plt.savefig(os.path.join(OUTPUT_DIR, 'torque_comparison_paper.png'), dpi=300, bbox_inches='tight')
    print(f"Comparison plot saved to {os.path.join(OUTPUT_DIR, 'torque_comparison_paper.png')}")

if __name__ == "__main__":
    plot_torque_comparison()
