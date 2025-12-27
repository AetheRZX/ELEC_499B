import numpy as np
import scipy.io
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

# --- Configuration ---
MAT_FILE = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files\phase_alignment_LUT.mat"
OUTPUT_FILE = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\figures\1_phase_alignment.png"

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

def plot_panel(ax, t_win, i_win, i_fund, e_win, label_suffix, show_legend=False):
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
        ax.legend(lns, labs, loc='upper right', frameon=True, fontsize=8)
        
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
fig, axes = plt.subplots(3, 1, figsize=(8, 10), constrained_layout=True)

points = [
    {'time': 0.41,  'label': '(a) Uncompensated'},
    {'time': 0.55, 'label': '(b) Filter Only'},
    {'time': 1.0,  'label': '(c) Filter + MTPA'}
]

# Calculate periods and offset
periods = []
for pt in points:
    w = np.interp(pt['time'], t, omega_r)
    periods.append(1/(w/(2*np.pi)) if w > 1 else 0.02)
max_period = max(periods)
align_offset = 0.6 * max_period 

saved_data = []

for i, pt in enumerate(points):
    target_t = pt['time']
    w_curr = np.interp(target_t, t, omega_r)
    f_curr = w_curr / (2*np.pi)
    period = 1/f_curr if f_curr > 0 else 0.01
    
    # Get broad filtered data
    broad_dur = 6 * period
    t_broad, i_broad, if_broad, _ = get_fundamental_chunk(t, i_as, omega_r, target_t, broad_dur)
    
    # Get corresponding e_as
    idx_s = np.searchsorted(t, t_broad[0])
    idx_e = idx_s + len(t_broad)
    e_broad = e_as[idx_s:idx_e]
    
    # Find ZC closest to target_t
    zcs = find_zero_crossing_falling(t_broad, e_broad)
    if len(zcs) == 0:
        continue
    ref_zc = zcs[np.argmin(np.abs(np.array(zcs) - target_t))]
    
    # Define window
    plot_start = ref_zc - align_offset
    plot_end = plot_start + 2.3 * period
    
    mask_final = (t_broad >= plot_start) & (t_broad <= plot_end)
    t_plot = t_broad[mask_final]
    i_plot = i_broad[mask_final]
    if_plot = if_broad[mask_final]
    e_plot = e_broad[mask_final]
    
    ax = axes[i]
    ax, ax2, t_r, i_r, if_r, e_r = plot_panel(ax, t_plot, i_plot, if_plot, e_plot, "", show_legend=(i==1))
    
    ax.text(0.02, 0.05, pt['label'], transform=ax.transAxes, fontsize=12, fontweight='bold', va='bottom', 
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=2))
    
    saved_data.append((t_r, i_r, if_r, e_r, ax, ax2))

# Use common ref_x
ref_x = align_offset * 1000

# (a) Uncompensated
t_a, i_a, if_a, e_a, ax_a, ax2_a = saved_data[0]
zc_i_rel = find_zero_crossing_falling(t_a, if_a)
if len(zc_i_rel) > 0:
    ci = zc_i_rel[np.argmin(np.abs(np.array(zc_i_rel) - ref_x))]
    ax_a.axvline(ref_x, color='k', linestyle='--', alpha=0.5)
    ax_a.axvline(ci, color='r', linestyle='--', alpha=0.5)

# (b) Filter Only
t_b, i_b, if_b, e_b, ax_b, ax2_b = saved_data[1]
zc_i_rel_b = find_zero_crossing_falling(t_b, if_b)
if len(zc_i_rel_b) > 0:
    ci_b = zc_i_rel_b[np.argmin(np.abs(np.array(zc_i_rel_b) - ref_x))]
    ax_b.axvline(ref_x, color='k', linestyle='--', alpha=0.5)
    ax_b.axvline(ci_b, color='r', linestyle='--', alpha=0.5)
    
    ylim = ax_b.get_ylim()
    y_text = ylim[1] * 0.7
    text_x = ci_b + 0.5 if ci_b > ref_x else ci_b - 2.5
    ax_b.annotate(r'$\Delta \phi_v$', xy=(ci_b, y_text), xytext=(text_x, y_text),
                 arrowprops=dict(arrowstyle='->', color='k'), fontsize=10)

# (c) Alignment
t_c, i_c, if_c, e_c, ax_c, ax2_c = saved_data[2]
ax_c.axvline(ref_x, color='r', linestyle='-.', alpha=0.8)
ylim = ax_c.get_ylim()
ax_c.text(ref_x + 0.3, ylim[1]*0.8, 'MTPA compensated', fontsize=10)

axes[2].set_xlabel('Time (ms)')
plt.savefig(OUTPUT_FILE, dpi=300)
print(f"Figure saved to {OUTPUT_FILE}")
