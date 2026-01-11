
import numpy as np
import matplotlib.pyplot as plt
import scipy.io
import os

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
OUTPUT_DIR = os.path.join(PARENT_DIR, 'figures')

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

MAT_FILES_V2 = os.path.join(PARENT_DIR, 'mat_files_v2')

FILES = {
    'LUT': os.path.join(MAT_FILES_V2, 'LUT_transient_voltage.mat'),
    '3-Step': os.path.join(MAT_FILES_V2, '3_step_transient_voltage.mat'),
    '6-Step': os.path.join(MAT_FILES_V2, '6_step_transient_voltage.mat')
}

LUT_ANGLES_DEG = np.array([56.0118, 58.0088, 66.0015, 56.0012, 58.0077, 66.0060])
# Note: User provided 6 angles.

class SpeedEstimator:
    def __init__(self, lut_vals_deg):
        self.t_prev_hw = None
        self.t_prev_sw = None
        # Initialize stores
        self.w_hw_store = 0.0
        self.w_hw_filt_store = 0.0
        self.w_sw_store = 0.0
        self.w_lut_store = 0.0
        self.dt_filt_store = 0.0
        
        self.prev_hall_state = 1
        self.prev_hw_trig = 0
        self.prev_sw_trig = 0
        
        self.PI_over_3 = np.pi / 3.0
        self.ALPHA = 0.05
        
        self.lut_vals_rad = np.deg2rad(lut_vals_deg)

    def update(self, timer, hw_trig, sw_trig, hall_state):
        # Convert inputs to simple types
        hw_trig = int(hw_trig)
        sw_trig = int(sw_trig)
        hall_state = int(hall_state)
        
        debug_angle = 0.0
        
        # Edge Detection
        trig_hw_now = (hw_trig > 0) and (self.prev_hw_trig == 0)
        trig_sw_now = (sw_trig > 0) and (self.prev_sw_trig == 0)
        
        self.prev_hw_trig = hw_trig
        self.prev_sw_trig = sw_trig
        
        if self.t_prev_hw is None:
             self.t_prev_hw = float(timer)
             self.t_prev_sw = float(timer)
             return 0, 0, 0, 0
        
        # --- HARDWARE ISR ---
        if trig_hw_now:
            dt_hw = float(timer) - self.t_prev_hw
            if dt_hw > 1e-6:
                # 1. Raw HW
                self.w_hw_store = self.PI_over_3 / dt_hw
                
                # 2. Filtered
                if self.dt_filt_store == 0:
                    self.dt_filt_store = dt_hw
                else:
                    self.dt_filt_store = (self.ALPHA * dt_hw) + ((1 - self.ALPHA) * self.dt_filt_store)
                
                self.w_hw_filt_store = self.PI_over_3 / self.dt_filt_store
                
                # 4. LUT Based
                # User Logic: idx = mod((prev_hall_state) + 2, 6)
                # Assumes prev_hall_state is 1-6??
                # Note: mod in python is %
                # If hall states are 1-6.
                # If we map hall indices to 0-5.
                # Let's try to match User Matrix Indexing.
                # If Hall State 1 -> Index ?
                # User: "phi_corr_LUT_param.Value" (list of 6)
                # Let's assume standard indexing.
                
                idx = (self.prev_hall_state - 1 + 2) % 6 
                # Explanation: prev_hall_state 1..6 -> 0..5. +2 -> shift. %6 -> wrap.
                
                actual_angle = self.lut_vals_rad[idx]
                
                self.w_lut_store = actual_angle / dt_hw
                
                self.t_prev_hw = float(timer)
                self.prev_hall_state = hall_state

        # --- SOFTWARE ISR ---
        if trig_sw_now:
             dt_sw = float(timer) - self.t_prev_sw
             if dt_sw > 1e-6:
                 self.w_sw_store = self.PI_over_3 / dt_sw
                 self.t_prev_sw = float(timer)
                 
        return self.w_hw_store, self.w_hw_filt_store, self.w_sw_store, self.w_lut_store

def run_estimation(file_label, path):
    if not os.path.exists(path):
        print(f"Skipping {file_label}, path not found: {path}")
        return
        
    print(f"Processing {file_label}...")
    try:
        mat = scipy.io.loadmat(path)
        time = mat['time'].flatten()
        theta_r = mat['theta_r'].flatten() if 'theta_r' in mat else None
        
        # Real Speed for comparison
        w_real = mat['rotor_speed'].flatten() if 'rotor_speed' in mat else (mat['omega_r'].flatten() if 'omega_r' in mat else None)

        if theta_r is None:
            print(f"No theta_r in {file_label}")
            return

        # Derive Hall State and Triggers
        # Hall State: 1..6 based on theta_r
        # Wrap to 0..2pi
        theta_wrapped = np.mod(theta_r, 2*np.pi)
        # Sectors: 0-60 -> 1, 60-120 -> 2...
        hall_states = np.floor(theta_wrapped / (np.pi/3)).astype(int) + 1
        hall_states[hall_states > 6] = 6 # floating point safety
        
        # Generate HW Trigger (rising edge of hall state change)
        # Actually any change in hall state is a trigger
        hw_trigs = np.zeros_like(hall_states, dtype=int)
        # Find changes
        diffs = np.diff(hall_states, prepend=hall_states[0])
        hw_trigs[diffs != 0] = 1
        
        # SW Trigger - User MAT file has software_ISR e.g. [0, 1].
        # If available use it, else mimic HW trigger or 1kHz?
        # User MAT inspection showed software_ISR is [0, 1].
        if 'software_ISR' in mat:
            sw_trigs = mat['software_ISR'].flatten()
        else:
            sw_trigs = np.zeros_like(time, dtype=int)
            
        estimator = SpeedEstimator(LUT_ANGLES_DEG)
        
        w_ests = []     # w_hw
        w_filts = []    # w_hw_filt
        w_luts = []     # w_lut
        
        for i in range(len(time)):
            w_h, w_f, w_s, w_l = estimator.update(time[i], hw_trigs[i], sw_trigs[i], hall_states[i])
            w_ests.append(w_h)
            w_filts.append(w_f)
            w_luts.append(w_l)
            
        # Plot
        plt.figure(figsize=(10, 6))
        plt.plot(time, w_real, 'k-', linewidth=2, label='Real Speed', alpha=0.6)
        plt.plot(time, w_ests, 'g--', linewidth=1, label='Raw HW Est')
        plt.plot(time, w_filts, 'b--', linewidth=1, label='Filtered HW Est')
        plt.plot(time, w_luts, 'r-', linewidth=1.5, label='LUT Est')
        
        plt.title(f'Speed Estimation Comparison - {file_label}')
        plt.xlabel('Time (s)')
        plt.ylabel('Speed (rad/s)')
        # Zoom to transient 1.0s
        plt.xlim([0.8, 1.2]) 
        # Or auto
        plt.legend()
        plt.grid(True)
        
        save_path = os.path.join(OUTPUT_DIR, f'speed_est_{file_label.replace(" ", "_")}.png')
        plt.savefig(save_path, dpi=300)
        print(f"Saved {save_path}")
        plt.close()

    except Exception as e:
        print(f"Error processing {file_label}: {e}")
        import traceback
        traceback.print_exc()

# Run for all 3 files
for label, path in FILES.items():
    run_estimation(label, path)
