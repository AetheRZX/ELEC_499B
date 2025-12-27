import numpy as np
import scipy.io
import matplotlib.pyplot as plt

# --- Configuration ---
MAT_FILE = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files\phase_alignment_LUT.mat"
OUTPUT_FILE = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\figures\2_tpa_comparison.png"

# --- Load Data ---
data = scipy.io.loadmat(MAT_FILE)
t = data['time'].flatten()
try:
    i_a = data['i_a'].flatten()
    e_a = data['e_a'].flatten()
    omega_r = data['omega_r'].flatten()
except KeyError as e:
    raise ValueError(f"Required keys not found: {e}")

def find_cycles(time, signal, min_freq=5.0):
    zcs = []
    min_period = 1.0 / min_freq
    last_t = -min_period
    for i in range(len(signal) - 1):
        if signal[i] <= 0 and signal[i+1] > 0:
            if time[i] - last_t > min_period * 0.5:
                frac = -signal[i] / (signal[i+1] - signal[i])
                zc_t = time[i] + frac * (time[i+1] - time[i])
                zcs.append((i, zc_t))
                last_t = zc_t
    return zcs

# --- Main Plotting ---
cases = [
    {'label': 'Uncompensated', 'time': 0.4,  'color': '#0072BD'}, 
    {'label': 'LUT Only',      'time': 0.55, 'color': '#EDB120'}, 
    {'label': 'LUT + MTPA',    'time': 1.0,  'color': '#D95319'}  
]

means = []
stds = []
labels = []
colors = []

POLE_PAIRS = 4

print("Calculating TPA Stats...")
for c in cases:
    t_start = c['time']
    duration = 0.2
    
    mask = (t >= t_start) & (t <= t_start + duration)
    t_win = t[mask]
    i_win = i_a[mask]
    e_win = e_a[mask]
    w_win = omega_r[mask]
    
    if len(i_win) > 100:
        I_rms = np.sqrt(np.mean(i_win**2))
        
        # Power Method: P = 3 * mean(e*i)
        P_avg = 3.0 * np.mean(e_win * i_win)
        
        # Mechanical Speed
        w_m_avg = np.mean(w_win) / POLE_PAIRS
        
        if abs(w_m_avg) > 1e-3:
            T_avg = P_avg / w_m_avg
        else:
            T_avg = 0
            
        if I_rms > 0.01:
            ratio = T_avg / I_rms
        else:
            ratio = 0
            
        means.append(abs(ratio))
        
        # Cycles
        idx_cycles = find_cycles(t_win, i_win)
        cycle_ratios = []
        for k in range(len(idx_cycles)-1):
            s, e = idx_cycles[k][0], idx_cycles[k+1][0]
            ic = i_win[s:e]
            ec = e_win[s:e]
            wc = w_win[s:e]
            if len(ic) > 5:
                Irms_c = np.sqrt(np.mean(ic**2))
                Pavg_c = np.mean(3.0 * ec * ic)
                w_mc = np.mean(wc) / POLE_PAIRS
                
                if Irms_c > 0.01 and abs(w_mc) > 1e-3:
                    cycle_ratios.append(abs((Pavg_c/w_mc)/Irms_c))
                    
        if len(cycle_ratios) > 2:
            stds.append(np.std(cycle_ratios))
        else:
            stds.append(0)
    else:
        means.append(0)
        stds.append(0)
        
    labels.append(c['label'])
    colors.append(c['color'])
    print(f"{c['label']}: {means[-1]:.4f} +/- {stds[-1]:.4f}")

fig, ax = plt.subplots(figsize=(6, 5), constrained_layout=True)

x_pos = np.arange(len(cases))
bar_width = 0.6

rects = ax.bar(x_pos, means, yerr=stds, width=bar_width, align='center', 
               color=colors, alpha=0.9, capsize=8, edgecolor='k')

ax.set_ylabel(r'Torque Constant $K_t$ (N$\cdot$m/A rms)', fontsize=12)
ax.set_xticks(x_pos)
ax.set_xticklabels(labels, fontsize=11, fontweight='bold')
ax.yaxis.grid(True, linestyle='--', alpha=0.6)

for rect, m in zip(rects, means):
    height = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., height + 0.0005,
            f'{m:.4f}',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

# Zoom in
ax.set_ylim([0.160, 0.180]) 

plt.savefig(OUTPUT_FILE, dpi=300)
print(f"Figure saved to {OUTPUT_FILE}")
