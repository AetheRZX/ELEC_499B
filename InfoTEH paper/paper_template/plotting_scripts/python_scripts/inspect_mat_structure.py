
import scipy.io
import numpy as np

file_path = r'd:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files_v2\LUT_torque_transient.mat'

try:
    mat = scipy.io.loadmat(file_path)
    with open('inspect_result_py.txt', 'w') as f:
        f.write(f"Keys in {file_path}: {list(mat.keys())}\n")
        if 'hardware_ISR' in mat:
            hw_isr = mat['hardware_ISR']
            f.write(f"hardware_ISR shape: {hw_isr.shape}\n")
            f.write(f"hardware_ISR unique: {np.unique(hw_isr)}\n")
            
        if 'software_ISR' in mat:
            sw_isr = mat['software_ISR']
            f.write(f"software_ISR shape: {sw_isr.shape}\n")
            f.write(f"software_ISR unique: {np.unique(sw_isr)}\n")
            
        if 'time' in mat:
            f.write(f"time shape: {mat['time'].shape}\n")
            
        if 'rotor_speed' in mat:
            f.write(f"rotor_speed shape: {mat['rotor_speed'].shape}\n")
        elif 'omega_r' in mat:
            f.write(f"omega_r shape: {mat['omega_r'].shape}\n")
            
        if 'T_e' in mat:
            te = mat['T_e']
            f.write(f"T_e shape: {te.shape}\n")
            f.write(f"T_e min: {np.min(te)}, max: {np.max(te)}, mean: {np.mean(te)}\n")
        else:
            f.write("T_e not found in MAT.\n")

except Exception as e:
    print(f"Error reading MAT file: {e}")
