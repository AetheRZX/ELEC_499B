import numpy as np
import scipy.io
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

# --- Configuration ---
MAT_FILE = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files\phase_alignment_LUT.mat"
OUTPUT_FILE = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\figures\0_intro_misalignment.png"

COLORS = {
    'i_as': '#005A9C',       # Blue
    'i_as_fund': '#C70039',  # Red
    'e_as': 'k'              # Black (dashed)
}

# --- Load Data ---
data = scipy.io.loadmat(MAT_FILE)
t = data['time'].flatten()
try:
    i_as = data['i_a'].flatten()
    e_as = data['e_a'].flatten()
    omega_r = data['omega_r'].flatten()
except KeyError:
    raise ValueError(f"Required keys not found. Available: {data.keys()}")

# --- Helper Functions ---
def get_fundamental_chunk(t_full, i_full, omega_full, target_time, plot_duration):
    w_est = np.interp(target_time, t_full, omega_full)
    f_est = w_est / (2 * np.pi)
    if f_est < 1: f_est = 1
    T_est = 1 / f_est
    
    pad_duration = max(0.15, 10 * T_est) 
    
    t_start_pad = target_time - pad_duration
    t_end_pad = target_time + plot_duration + pad_duration
    
    mask_pad = (t_full >= t_start_pad) & (t_full <= t_end_pad)
    t_chunk = t_full[mask_pad]
    i_chunk = i_full[mask_pad]
    
    if len(t_chunk) == 0:
        return None, None, None, None
        
    dt = np.mean(np.diff(t_chunk))
    fs = 1 / dt
    
    low = (f_est * 0.5) / (0.5 * fs)
    high = (f_est * 1.5) / (0.5 * fs)

    b, a = butter(2, [low, high], btype='band')
    i_fund_chunk = filtfilt(b, a, i_chunk)
    
    mask_plot = (t_chunk >= target_time) & (t_chunk <= target_time + plot_duration)
    
    return t_chunk, i_chunk, i_fund_chunk, mask_pad

def plot_panel(ax, t_win, i_win, i_fund, e_win, label_suffix, show_legend=False, legend_loc='upper right'):
    t_plot = (t_win - t_win[0]) * 1000 # ms
    
    max_i = np.max(np.abs(i_win)) if len(i_win) > 0 else 10
    max_e = np.max(np.abs(e_win)) if len(e_win) > 0 else 10
    
    lim_i = max_i * 1.3
    lim_e = max_e * 1.3
    
    lns1 = ax.plot(t_plot, i_win, color=COLORS['i_as'], label='$i_{as}$', linewidth=1.5)
    lns2 = ax.plot(t_plot, i_fund, color=COLORS['i_as_fund'], label='$i_{as,fund}$', linewidth=1.5)
    ax.set_ylim([-lim_i, lim_i])
    ax.set_ylabel('Current (A)')
    
    ax2 = ax.twinx()
    lns3 = ax2.plot(t_plot, e_win, color=COLORS['e_as'], linestyle='--', label='$e_{as}$', linewidth=1.5)
    ax2.set_ylim([-lim_e, lim_e])
    
    ax2.set_ylabel('Back EMF (V)')
    
    if show_legend:
        lns = lns1 + lns2 + lns3
        labs = [l.get_label() for l in lns]
        ax.legend(lns, labs, loc=legend_loc, frameon=True, fontsize=8)
        
    ax.grid(True, linestyle=':', alpha=0.6)
    
    return ax, ax2, t_plot, i_win, i_fund, e_win

def find_zero_crossing_falling(time, y):
    crossings = []
    for i in range(len(y)-1):
        if y[i] > 0 and y[i+1] <= 0:
            frac = y[i] / (y[i] - y[i+1])
            crossings.append(time[i] + frac * (time[i+1] - time[i]))
    return crossings

# --- Main Plotting ---
fig, ax = plt.subplots(1, 1, figsize=(8, 4), constrained_layout=True)

# Single point - Uncompensated
target_t = 0.41

w_curr = np.interp(target_t, t, omega_r)
f_curr = w_curr / (2*np.pi)
period = 1/f_curr if f_curr > 0 else 0.01

align_offset = 0.6 * period 

broad_dur = 6 * period
t_broad, i_broad, if_broad, _ = get_fundamental_chunk(t, i_as, omega_r, target_t, broad_dur)

idx_s = np.searchsorted(t, t_broad[0])
idx_e = idx_s + len(t_broad)
e_broad = e_as[idx_s:idx_e]

zcs = find_zero_crossing_falling(t_broad, e_broad)
if len(zcs) > 0:
    ref_zc = zcs[np.argmin(np.abs(np.array(zcs) - target_t))]
    
    plot_start = ref_zc - align_offset
    plot_end = plot_start + 2.3 * period
    
    mask_final = (t_broad >= plot_start) & (t_broad <= plot_end)
    t_plot = t_broad[mask_final]
    i_plot = i_broad[mask_final]
    if_plot = if_broad[mask_final]
    e_plot = e_broad[mask_final]
    
    # Plot - Legend lower right by default for single plot?
    ax, ax2, t_r, i_r, if_r, e_r = plot_panel(ax, t_plot, i_plot, if_plot, e_plot, "", show_legend=True, legend_loc='lower right')
    
    # Label REMOVED

    # Add Misalignment Annotation
    ref_x = align_offset * 1000
    zc_i_rel = find_zero_crossing_falling(t_r, if_r)
    
    if len(zc_i_rel) > 0:
        ci = zc_i_rel[np.argmin(np.abs(np.array(zc_i_rel) - ref_x))]
        ax.axvline(ref_x, color='k', linestyle='--', alpha=0.5)
        ax.axvline(ci, color='r', linestyle='--', alpha=0.5)
        
        ylim = ax.get_ylim()
        y_text = ylim[1] * 0.7
        text_x = ci + 0.5 if ci > ref_x else ci - 2.5
        ax.annotate(r'$\Delta \phi$', xy=(ci, y_text), xytext=(text_x, y_text),
                    arrowprops=dict(arrowstyle='->', color='k'), fontsize=10)

ax.set_xlabel('Time (ms)')
plt.savefig(OUTPUT_FILE, dpi=300)
print(f"Figure saved to {OUTPUT_FILE}")
