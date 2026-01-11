import scipy.io
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

# --- CONFIGURATION ---
DATA_FOLDER = Path('mat_files_v2')
OUTPUT_FOLDER = Path('figures')

# Enter the name of the file you saved in MATLAB (without .mat)
FILENAME = 'hall_sensor_run' 

# Time settings for the plot view
FILTER_ACTIVATION_TIME = 0.5  # When the logic changes
WINDOW_SIZE = 0.03            # +/- seconds to show around the event (Increased slightly for text space)

def get_aligned_time(ref_time, data_signal):
    """Generates synthetic time vector if lengths mismatch."""
    len_t = len(ref_time)
    len_d = len(data_signal)
    if len_t == len_d: return ref_time
    return np.linspace(ref_time[0], ref_time[-1], len_d)

def plot_hall_comparison():
    file_path = DATA_FOLDER / f"{FILENAME}.mat"
    
    if not file_path.exists():
        print(f"Error: File {file_path} not found.")
        print("Please run the MATLAB script and ensure the tag matches.")
        return

    try:
        data = scipy.io.loadmat(str(file_path), squeeze_me=True)
    except Exception as e:
        print(f"Error loading mat file: {e}")
        return

    # Extract Data
    raw_time = data['time']
    perfect_hall = data['perfect_hall']
    result_hall = data['result_hall']

    # Align Time Vectors
    t_perfect = get_aligned_time(raw_time, perfect_hall)
    t_result = get_aligned_time(raw_time, result_hall)

    # --- PLOTTING ---
    fig, ax = plt.subplots(figsize=(10, 5))

    # Plot Perfect Hall (Blue)
    ax.step(t_perfect, perfect_hall, where='post', 
            label='Perfect Hall State', color='#2980b9', linewidth=2.5, alpha=0.6)

    # Plot Result State (Red/Orange)
    ax.step(t_result, result_hall, where='post', 
            label='Actual Hall State', color='#e74c3c', linewidth=2)

    # --- Formatting ---
    
    # Zoom limits
    t_start = FILTER_ACTIVATION_TIME - WINDOW_SIZE
    t_end = FILTER_ACTIVATION_TIME + WINDOW_SIZE
    ax.set_xlim(t_start, t_end)

    # Y-Axis (States 1-6) - Increased Max to 7.5 to fit arrows
    ax.set_ylim(0.5, 7.5) 
    ax.set_yticks([1, 2, 3, 4, 5, 6])
    ax.set_ylabel('Hall State', fontsize=12)
    ax.set_xlabel('Time (s)', fontsize=12)
    # ax.set_title('Comparison of Perfect vs. Filtered Hall States', fontsize=14)

    # --- THE "NO FILTER <---|---> FILTER APPLIED" VISUAL ---
    
    # 1. Vertical Dashed Line
    ax.axvline(x=FILTER_ACTIVATION_TIME, color='gray', linestyle='--', linewidth=2, alpha=0.8)

    # Y-position for the arrows/text
    y_arrow_pos = 7.0 
    arrow_len = WINDOW_SIZE * 0.15 # Dynamic arrow length based on zoom

    # 2. Left Arrow (<---)
    ax.annotate('', 
                xy=(FILTER_ACTIVATION_TIME - arrow_len, y_arrow_pos), # Arrow Tip
                xytext=(FILTER_ACTIVATION_TIME, y_arrow_pos),         # Arrow Start (at line)
                arrowprops=dict(arrowstyle="->", color='black', lw=1.5))

    # 3. Right Arrow (--->)
    ax.annotate('', 
                xy=(FILTER_ACTIVATION_TIME + arrow_len, y_arrow_pos), # Arrow Tip
                xytext=(FILTER_ACTIVATION_TIME, y_arrow_pos),         # Arrow Start (at line)
                arrowprops=dict(arrowstyle="->", color='black', lw=1.5))

    # 4. Text Labels
    ax.text(FILTER_ACTIVATION_TIME - arrow_len - 0.002, y_arrow_pos, 
            "No Filter", 
            ha='right', va='center', fontsize=12, fontweight='bold', color='black')

    ax.text(FILTER_ACTIVATION_TIME + arrow_len + 0.002, y_arrow_pos, 
            "Filter Applied", 
            ha='left', va='center', fontsize=12, fontweight='bold', color='black')

    # Grid and Legend
    ax.grid(True, linestyle='--', alpha=0.5)
    # Move legend to bottom right to avoid blocking the top text
    ax.legend(loc='upper left', framealpha=1, edgecolor='black')

    # Save
    if not OUTPUT_FOLDER.exists(): OUTPUT_FOLDER.mkdir(parents=True)
    out_name = OUTPUT_FOLDER / 'Hall_State_before_after.png'
    plt.savefig(out_name, dpi=300, bbox_inches='tight')
    print(f"Saved figure to {out_name}")
    plt.show()

if __name__ == "__main__":
    plot_hall_comparison()