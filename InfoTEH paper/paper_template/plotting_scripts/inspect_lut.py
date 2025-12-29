import scipy.io
FILE = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\plotting_scripts\mat_files\LUT_from_startup.mat"
data = scipy.io.loadmat(FILE)
print("Keys:", [k for k in data.keys() if not k.startswith('__')])
