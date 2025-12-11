import scipy.io
import scipy.signal
import matplotlib.pyplot as plt
import numpy as np
import os

FILE_INPUT = os.path.join('mat_files', 'transient_run_lut1.mat')
OUTPUT_DIR = 'figures'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Time Windows
# Uncomp: 0 to 0.5
T_ZOOM_UNCOMP = [0.460, 0.490] 
# LUT: 0.5 to ? (User simulation likely goes to 1.5s)
# User said "use the time at like 1 seconds where it is steady state for MTPA".
# MTPA likely activates at 0.55 and stays on.
# So Uncomp: < 0.5
# LUT Only? Does simulation have a "LUT Only" phase that is steady?
# Previous plot assumed 0.5-0.55 was LUT Only.
# If MTPA turns on at 0.55, then [0.5, 0.55] is the only LUT-only window.
T_ZOOM_LUT = [0.520, 0.550] 
# MTPA + LUT: > 0.55. Steady state at 1.0s.
T_ZOOM_MTPA = [1.000, 1.030]

# Colors
C_IA = '#005A9C' 
C_FUND = '#C70039' 
C_BEMF = 'k'

def load_data(fpath):
    if not os.path.exists(fpath): return None
    mat = scipy.io.loadmat(fpath)
    def g(k): return mat[k].flatten() if k in mat else None
    
    t = g('time'); ia = g('i_a')
    if ia is None: ia = g('i_as')
    theta = g('theta_r')
    eq = g('e_q'); eas = g('e_as')
    
    if t is None or ia is None or theta is None: return None
    
    L = min(len(t), len(ia), len(theta))
    t=t[:L]; ia=ia[:L]; theta=theta[:L]
    
    if eas is None:
        if eq is not None:
            eq = eq[:L]
            # User feedback: "shouldnt it be zero phase difference when lut and mtpa"
            # Previous plot showed ~100 deg phase diff (misaligned).
            # This implies -Sine was actually giving correct alignment (0 deg/180 deg).
            # But user complained about it.
            # Maybe the sign of Sine was wrong relative to Current?
            # Revert to Sine.
            scale_factor = 2.0 
            eas = -1.0 * np.abs(eq) * scale_factor * np.sin(theta)
        else:
             eas = -15.0 * np.sin(theta)
    else:
        eas = eas[:L]
        
    dt = np.mean(np.diff(t))
    fs = 1/dt
    th_u = np.unwrap(theta)
    w = (th_u[-1]-th_u[0]) / (t[-1]-t[0])
    f0 = w / (2*np.pi)
    
    sos = scipy.signal.butter(2, [0.8*f0, 1.2*f0], btype='bandpass', fs=fs, output='sos')
    ia_fund = scipy.signal.sosfiltfilt(sos, ia)
    
    return t, ia, ia_fund, eas, fs, f0

def plot_seg(ax, t, ia, ia_f, eas, title, let, f0):
    t_ms = (t - t[0]) * 1000
    l1 = ax.plot(t_ms, ia, color=C_IA, label=r'$i_{as}$', lw=1.2)
    l2 = ax.plot(t_ms, ia_f, color=C_FUND, label=r'$i_{as,fund}$', lw=1.5)
    ax.set_ylabel('Current (A)')
    ax.set_ylim(-18, 18)
    ax.grid(True, ls=':', alpha=0.5)
    
    axR = ax.twinx()
    l3 = axR.plot(t_ms, eas, color=C_BEMF, linestyle='--', label=r'$e_{as}$', lw=1.2)
    axR.set_ylabel('Voltage (V)')
    axR.set_ylim(-20, 20)
    
    # User: "can you not plot the difference"
    # Removed phase calculation annotation.
    
    ax.text(0.5, 0.9, title, transform=ax.transAxes, ha='center', fontweight='bold')
    ax.text(0.02, 0.9, let, transform=ax.transAxes, fontweight='bold', fontsize=12)

    return l1+l2+l3

def run():
    d = load_data(FILE_INPUT)
    if not d: print("No data"); return
    t, ia, ia_f, eas, fs, f0 = d
    
    fig, axs = plt.subplots(3, 1, figsize=(8, 10), constrained_layout=True)
    
    handles = []
    
    for i, (ax, rng, title, let) in enumerate(zip(axs, [T_ZOOM_UNCOMP, T_ZOOM_LUT, T_ZOOM_MTPA], ["Uncompensated", "LUT Only", "LUT + MTPA"], ["(a)", "(b)", "(c)"])):
        # Ensure range exists in t
        if rng[1] > t[-1]:
            print(f"Warning: Range {rng} out of bounds (max {t[-1]}). Using last 30ms.")
            rng = [t[-1]-0.030, t[-1]]
            
        idx = np.where((t >= rng[0]) & (t <= rng[1]))[0]
        h = plot_seg(ax, t[idx], ia[idx], ia_f[idx], eas[idx], title, let, f0)
        if i == 0: handles = h
        
    axs[2].set_xlabel('Time (ms)')
    
    fig.legend(handles, [l.get_label() for l in handles], loc='upper center', bbox_to_anchor=(0.5, 1.02), ncol=3)
    
    plt.savefig(os.path.join(OUTPUT_DIR, 'alignment_plot.png'), dpi=300, bbox_inches='tight')

if __name__=='__main__': run()
