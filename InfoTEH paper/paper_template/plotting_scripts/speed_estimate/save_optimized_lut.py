
import numpy as np
import scipy.io as sio
from pathlib import Path

# Ideal M3 LUT Values (Degrees)
# Derived from fix_oscillation.py results
ideal_m3_deg = np.array([
    [65.9811],
    [48.4872],
    [65.4842],
    [65.9832],
    [48.4878],
    [65.4765]
])

# Use radians if that's what the Simulink model expects internally, 
# but the user prompt implies they are looking at these numbers (which look like degrees).
# Wait, previous interaction: "M2 LUT values (Radians -> Degrees)".
# The User GAVE me radians earlier: "0.9541" which is ~54 deg.
# The user asked "make it into this phi_corr_LUT_param.Value".
# The numbers they pasted "65.9811" are DEGREES.
# Does the `phi_corr_LUT_param.Value` expect DEGREES or RADIANS?
# The original file inspection showed complex binary data. 
# But in `speed_estimate.py`, I converted the user's radians to degrees for plotting.
# IF the Simulink model uses these values, it almost certainly expects the same unit as the original.
# The original Default LUT was `[55.998, ...]`. These are clearly DEGREES. 
# (56 radians is ~9 rotations, makes no sense for a sector).
# SO: The parameter expects DEGREES.

OUTPUT_DIR = Path(r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files")
FILE_NAME = OUTPUT_DIR / "Hall_LUT_Config_M3_Optimized.mat"

# Create dictionary to save
# We save it as a simple variable 'lut_values_optimized' 
# AND also try to save it as 'phi_corr_LUT_param' (simpler struct version) in case that helps.
data = {
    "lut_values_optimized": ideal_m3_deg,
    "phi_corr_LUT_param_value": ideal_m3_deg # Helper variable
}

print(f"Saving to {FILE_NAME}...")
sio.savemat(FILE_NAME, data)
print("Done.")
