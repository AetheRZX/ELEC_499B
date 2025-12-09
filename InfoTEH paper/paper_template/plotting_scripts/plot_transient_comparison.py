import scipy.io
import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.linear_model import LinearRegression

# Configuration
FILE_LUT0 = os.path.join('mat_files', 'transient_run_lut0.mat')
FILE_LUT1 = os.path.join('mat_files', 'transient_run_lut1.mat')
OUTPUT_DIR = 'figures'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Timings (Sim time)
T_SIM_FILTER = 0.50
T_SIM_MTPA = 0.55
T_START_OFFSET = 0.48

# Plot Ranges (ms)
T_DETAIL_XMIN = -10 # Padding for Uncompensated
T_DETAIL_MAX_MS = 140
T_DECAY_MAX_MS = 400

time_scale = 1000.0

def load_data(fpath):
    if not os.path.exists(fpath): return None
    mat = scipy.io.loadmat(fpath)
    def g(keys):
        for k in keys:
            if k in mat: return mat[k].flatten()
        return np.array([])
    t = g(['time', 't'])
    ia = g(['i_a', 'i_as'])
    ids = g(['i_ds']) 
    ids_avg = g(['i_ds_avg'])
    
    if len(ids) == 0:
        L = min(len(t), len(ia), len(ids_avg))
        ids = np.zeros(L)
    else:
        L = min(len(t), len(ia), len(ids_avg), len(ids))
        ids = ids[:L]
    return t[:L], ia[:L], ids, ids_avg[:L]

def calculate_tau(t_ms, y):
    # Fit decay from peak (approx 75ms) to end
    start_ms = 80 
    end_ms = 350
    mask = (t_ms >= start_ms) & (t_ms <= end_ms) & (y > 0.1)
    
    if np.sum(mask) < 10: return None
    
    t_fit = t_ms[mask]
    y_fit = y[mask]
    
    model = LinearRegression()
    X = t_fit.reshape(-1, 1)
    Y = np.log(y_fit)
    model.fit(X, Y)
    
    slope = model.coef_[0]
    tau_ms = -1.0 / slope
    return tau_ms

def plot_row(ax_detail, ax_decay, t, i_a, i_ds, i_ds_avg, title_labels, letter):
    t_ms = (t - T_START_OFFSET) * time_scale
    
    c_ia = '#005A9C'
    c_ids = '#C70039'
    
    # --- LEFT: DETAIL ---
    ax_detail.plot(t_ms, i_a, color=c_ia, linewidth=1.2, label=r'$i_{as}$')
    ax_detail.plot(t_ms, i_ds, color=c_ids, linewidth=1.2, label=r'$i_{ds}$')
    ax_detail.plot(t_ms, i_ds_avg, color='k', linewidth=2.0, label=r'$\bar{i}_{ds}$')
    
    t_filter = (T_SIM_FILTER - T_START_OFFSET)*1000
    t_mtpa = (T_SIM_MTPA - T_START_OFFSET)*1000
    ax_detail.axvline(t_filter, color='k', linestyle='-.', lw=1.5)
    ax_detail.axvline(t_mtpa, color='k', linestyle='-.', lw=1.5)
    
    ax_detail.set_xlim(T_DETAIL_XMIN, T_DETAIL_MAX_MS)
    ax_detail.set_ylim(-22, 24) # Increased padding
    
    # Labels
    y_txt = 21 # Moved up
    # Adjust center points for labels considering -10 start? No, labels are at specific times.
    ax_detail.text(t_filter/2, y_txt, title_labels[0], ha='center', fontsize=10, fontweight='bold')
    ax_detail.text((t_filter+t_mtpa)/2, y_txt, title_labels[1], ha='center', fontsize=10, fontweight='bold')
    ax_detail.text((t_mtpa+T_DETAIL_MAX_MS)/2, y_txt, title_labels[2], ha='center', fontsize=10, fontweight='bold')
    
    ax_detail.text(-0.1, 1.05, letter, transform=ax_detail.transAxes, fontsize=14, fontweight='bold')
    ax_detail.set_ylabel('Current (A)', fontsize=12)
    ax_detail.grid(True, linestyle=':', alpha=0.5)
    
    # Break Marks (Right spine)
    d = .015 
    kwargs = dict(transform=ax_detail.transAxes, color='k', clip_on=False)
    ax_detail.plot((1-d, 1+d), (-d, +d), **kwargs) 
    ax_detail.plot((1-d, 1+d), (1-d, 1+d), **kwargs) 
    ax_detail.spines['right'].set_visible(False)

    # --- RIGHT: DECAY ---
    ax_decay.plot(t_ms, i_a, color=c_ia, linewidth=1.2)
    ax_decay.plot(t_ms, i_ds, color=c_ids, linewidth=1.2)
    ax_decay.plot(t_ms, i_ds_avg, color='k', linewidth=2.0)
    
    ax_decay.set_xlim(0, T_DECAY_MAX_MS)
    ax_decay.set_ylim(-22, 24) # Match Left
    
    # Break Marks (Left spine)
    kwargs.update(transform=ax_decay.transAxes) 
    ax_decay.plot((-d, +d), (-d, +d), **kwargs) 
    ax_decay.plot((-d, +d), (1-d, 1+d), **kwargs) 
    ax_decay.spines['left'].set_visible(False)
    ax_decay.yaxis.tick_right() 
    
    ax_decay.grid(True, linestyle=':', alpha=0.5)

    return

def plot_all():
    d0 = load_data(FILE_LUT0)
    d1 = load_data(FILE_LUT1)
    if d0 is None or d1 is None: print("Data missing"); return
    
    # --- Figure 1: Split Panels ---
    fig, axes = plt.subplots(2, 2, figsize=(14, 6), constrained_layout=True, 
                             gridspec_kw={'width_ratios': [2, 1]})
    
    plot_row(axes[0,0], axes[0,1], *d0, ["Uncompensated", "Filter Only", "Filter + MTPA"], '(a)')
    plot_row(axes[1,0], axes[1,1], *d1, ["Uncompensated", "LUT Only", "LUT + MTPA"], '(b)')
    
    axes[1,0].set_xlabel('Time (ms)', fontsize=12)
    axes[1,1].set_xlabel('Time (ms)', fontsize=12)
    
    handles, labels = axes[1,0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.05))
    
    out = os.path.join(OUTPUT_DIR, 'current_transient_stacked_inset.png')
    plt.savefig(out, dpi=300, bbox_inches='tight')
    print(f"Saved {out}")
    
    # --- Figure 2: Compare Plot ---
    t0, _, _, avg0 = d0
    _, _, _, avg1 = d1 
    L = min(len(avg0), len(avg1))
    
    t0_ms = (t0[:L] - T_START_OFFSET)*1000
    avg0 = avg0[:L]
    avg1 = avg1[:L]
    diff = avg1 - avg0
    
    tau0 = calculate_tau(t0_ms, avg0)
    tau1 = calculate_tau(t0_ms, avg1)
    
    fig2, (ax_main, ax_diff) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, constrained_layout=True, gridspec_kw={'height_ratios': [2, 1]})
    
    c_blue = '#005A9C'
    c_red = '#C70039'
    
    ax_main.plot(t0_ms, avg0, color=c_blue, label=r'Filter $\bar{i}_{ds}$')
    ax_main.plot(t0_ms, avg1, color=c_red, linestyle='--', label=r'LUT $\bar{i}_{ds}$')
    ax_main.set_ylabel(r'$\bar{i}_{ds}$ (A)')
    ax_main.grid(True)
    
    txt = r""
    if tau0: txt += f"Filter $\\tau \\approx {tau0:.1f}$ ms\n"
    if tau1: txt += f"LUT $\\tau \\approx {tau1:.1f}$ ms"
    if txt:
        ax_main.text(0.6, 0.6, txt, transform=ax_main.transAxes, fontsize=12, 
                     bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

    ax_main.legend(loc='upper right')
    ax_main.set_ylim(-0.5, 5) 
    ax_main.set_xlim(0, T_DECAY_MAX_MS)
    
    ax_diff.plot(t0_ms, diff, 'k', linewidth=1.2, label=r'Diff (LUT - Filter)')
    
    t_f = (T_SIM_FILTER-T_START_OFFSET)*1000
    t_m = (T_SIM_MTPA-T_START_OFFSET)*1000
    ax_diff.axvline(t_f, color='k', ls='-.', alpha=0.5)
    ax_diff.axvline(t_m, color='k', ls='-.', alpha=0.5)
    
    ax_diff.set_ylabel(r'error (A)')
    ax_diff.set_xlabel('Time (ms)')
    ax_diff.set_xlim(0, T_DECAY_MAX_MS)
    ax_diff.grid(True)
    ax_diff.set_ylim(min(diff)*1.1, max(diff)*1.1)

    out2 = os.path.join(OUTPUT_DIR, 'current_transient_compare.png')
    plt.savefig(out2, dpi=300)
    print(f"Saved {out2}")

if __name__ == "__main__":
    plot_all()
