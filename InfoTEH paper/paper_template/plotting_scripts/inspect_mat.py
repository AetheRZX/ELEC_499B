import scipy.io

mat_file = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files\phase_alignment_LUT.mat"
data = scipy.io.loadmat(mat_file)

keys = [k for k in data.keys() if not k.startswith('__')]
print("Available keys:", keys)
