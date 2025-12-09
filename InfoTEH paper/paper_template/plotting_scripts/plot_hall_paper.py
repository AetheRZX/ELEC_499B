import scipy.io
import matplotlib.pyplot as plt
import numpy as np
import os

# Configuration
DATA_FILE = os.path.join('mat_files', 'hall_data_extracted.mat')
OUTPUT_DIR = 'figures'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'hall_sensor_comparison_paper.png')

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def plot_hall_paper():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found.")
        return

    mat = scipy.io.loadmat(DATA_FILE)
    t = mat['time'].flatten()
    h1, h2, h3 = mat['H1'].flatten(), mat['H2'].flatten(), mat['H3'].flatten()
    h1_i, h2_i, h3_i = mat['H1_ideal'].flatten(), mat['H2_ideal'].flatten(), mat['H3_ideal'].flatten()

    # --- Derive States ---
    th = 0.5
    s1, s2, s3 = (h1 > th).astype(int), (h2 > th).astype(int), (h3 > th).astype(int)
    total_state_raw = s1*4 + s2*2 + s3
    
    trans_idxs = np.where(np.diff(total_state_raw) != 0)[0] + 1
    trans_idxs = np.concatenate(([0], trans_idxs, [len(t)-1]))
    
    raw_segments = []
    for i in range(len(trans_idxs)-1):
        dur = t[trans_idxs[i+1]] - t[trans_idxs[i]]
        idx_mid = (trans_idxs[i] + trans_idxs[i+1]) // 2
        val = total_state_raw[idx_mid]
        st = ( (val>>2)&1, (val>>1)&1, (val&1) )
        if dur > 0.0005: 
             raw_segments.append({'start': trans_idxs[i], 'end': trans_idxs[i+1], 'tuple': st, 'dur_t': dur})
    
    clean_segments = raw_segments
    
    # Labeling
    pixel_labels = [''] * len(clean_segments)
    anchor_idx = -1
    for i in range(1, len(clean_segments)):
        if clean_segments[i-1]['tuple'][0] == 1 and clean_segments[i]['tuple'][0] == 0:
            pixel_labels[i] = 'II'
            anchor_idx = i
            break
            
    if anchor_idx != -1:
        seq = ['I', 'II', 'III', 'IV', 'V', 'VI']
        for i in range(len(clean_segments)):
            if i == anchor_idx: continue
            dist = i - anchor_idx
            seq_idx = (1 + dist) % 6
            pixel_labels[i] = seq[seq_idx]
    
    # --- PLOTTING ---
    fig, axes = plt.subplots(4, 1, figsize=(10, 5), sharex=True, 
                             gridspec_kw={'height_ratios': [1, 1, 1, 0.4], 'hspace': 0})
    
    c_h1 = '#EDB120'; c_h2 = '#0072BD'; c_h3 = '#D95319'
    lw_ideal, lw_act = 2.0, 2.0
    
    def plot_sig_color(ax, time, sig_i, sig, color, label, is_top=False):
        ax.plot(time, sig_i, color=color, linestyle=':', linewidth=lw_ideal, alpha=1.0)
        ax.plot(time, sig, color=color, linewidth=lw_act)
        ax.text(-0.02, 0.5, label, transform=ax.transAxes, fontsize=14, va='center', ha='right', fontstyle='italic')
        
        # Set Top Limit for consistent height, Bottom at 0 to touch the specific axis below
        # Signals allow 0 to 1.
        # If we set ylim(0, 1.2), y=0 is at axis bottom.
        ax.set_ylim(0, 1.25)
            
        ax.axis('off')
        # Draw Baseline at 0? It's effectively the axis border now.
        # But we turned off axis. So let's draw it precisely at y=0.
        ax.plot([time[0], time[-1]], [0, 0], 'k-', linewidth=1.0) # Matches sector line width

    plot_sig_color(axes[0], t, h1_i, h1, c_h1, r'$h_1$', is_top=True)
    plot_sig_color(axes[1], t, h2_i, h2, c_h2, r'$h_2$')
    plot_sig_color(axes[2], t, h3_i, h3, c_h3, r'$h_3$')
    
    # --- Vertical Grid Lines ---
    grid_times = [t[seg['start']] for seg in clean_segments if t[seg['start']] > t[0]+0.0001]
    for ax in axes:
        for gt in grid_times:
            # ymin=0, ymax=1 works for full height in axes coords
            # But we are in data coords for plotting? No axvline uses data x and 0-1 y-axis
            ax.axvline(gt, color='k', linestyle=':', linewidth=1.0, alpha=0.5)

    # --- Bottom Axis (Touching H3) ---
    ax_sec = axes[3]
    ax_sec.set_xlim(t[0], t[-1])
    ax_sec.set_ylim(0, 1)
    ax_sec.axis('off')
    
    # Top line of sector axis (merged with H3 baseline)
    # H3 baseline is at its bottom. Sector top is at its top.
    # Since hspace=0, they are coincident. 
    # H3 draws a line at y=0. Sector draws a line at y=1.
    ax_sec.plot([t[0], t[-1]], [1, 1], 'k-', linewidth=1.0)
    
    for i, seg in enumerate(clean_segments):
        start = max(t[seg['start']], t[0])
        end = min(t[seg['end']], t[-1])
        if i == len(clean_segments)-1: end = t[-1]
        
        is_left_cut = (start <= t[0] + 0.0001)
        is_right_cut = (end >= t[-1] - 0.0001)
        
        if end - start > 0.0005:
            # Style
            style = '<->'
            if is_left_cut and is_right_cut: style = '-'
            elif is_left_cut: style = '<-'
            elif is_right_cut: style = '->'
            
            y_ar = 0.5
            ax_sec.annotate('', xy=(start, y_ar), xytext=(end, y_ar),
                            arrowprops=dict(arrowstyle=style, color='k', lw=1.0))
            
            mid = (start+end)/2
            lbl = pixel_labels[i]
            # Use bbox to block line
            ax_sec.text(mid, 0.5, lbl, ha='center', va='center', fontsize=12, fontweight='bold',
                        bbox=dict(facecolor='white', edgecolor='none', pad=1.0))
    
    # Theta Label
    ax_sec.text(1.01, 0.5, r'$\theta_r$', transform=ax_sec.transAxes, 
                fontsize=14, va='center', ha='left')

    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
    print(f"Plot saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    plot_hall_paper()
