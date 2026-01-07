
import scipy.io
import numpy as np

def extract_lut(file_path):
    print(f"Reading {file_path}...")
    try:
        mat = scipy.io.loadmat(file_path)
        # Often these are stored as 'phi_corr_LUT_param' or similar keys.
        # But based on inspection it was a MatlabOpaque.
        # Let's look for known keys.
        for key in mat:
            if key.startswith('__'): continue
            val = mat[key]
            print(f"Key: {key}, Type: {type(val)}")
            
            # If it's a Simulink.Parameter, it might have a .item() that gives the value
            if 'MatlabOpaque' in str(type(val)):
                print("  Input is MatlabOpaque. Access logic is tricky.")
                # Sometimes we can see the internal array via inspection of 'arr' if we knew the structure
                # But scipy.io doesn't fully support Opaque. 
                # HOWEVER, sometimes there are other keys or we can just access .item() if it's a scalar object wrapping something.
                try:
                     # This is a shot in the dark for Opaque objects
                     # Sometime the 'Value' property is accessible if it was saved a certain way.
                     pass
                except:
                    pass
    except Exception as e:
        print(f"Error: {e}")

# Hardcoded back-up for Default (from speed_estimate.py)
# [55.998, 57.995, 65.991, 55.998, 57.994, 65.99]

if __name__ == "__main__":
    files = [
        r'd:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files\Hall_LUT_Config.mat',
        r'd:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files\Hall_LUT_Config_M2.mat',
        r'd:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files\Hall_LUT_Config_M3.mat'
    ]
    for f in files:
        extract_lut(f)
