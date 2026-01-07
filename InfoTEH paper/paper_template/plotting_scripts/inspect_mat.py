
import scipy.io
import os
import numpy as np

files = [
    r'd:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files\speed_estimation_test.mat',
    r'd:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files\Hall_LUT_Config.mat'
]

with open('mat_info.txt', 'w') as log:
    for f in files:
        log.write(f"--- Inspecting {os.path.basename(f)} ---\n")
        try:
            mat = scipy.io.loadmat(f)
            for key in mat:
                if not key.startswith('__'):
                    val = mat[key]
                    log.write(f"Key: {key}, Type: {type(val)}\n")
                    if hasattr(val, 'shape'):
                         log.write(f"  Shape: {val.shape}\n")
                    if hasattr(val, 'dtype'):
                         log.write(f"  Dtype: {val.dtype}\n")
                    
                    if hasattr(val, 'flat') and val.size < 20:
                        log.write(f"  Value: {val}\n")
                    elif hasattr(val, 'dtype') and val.dtype.names:
                        log.write(f"  Fields: {val.dtype.names}\n")
        except Exception as e:
            log.write(f"Error loading {f}: {e}\n")
