
fn = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\latex\IEEE-conference-template-062824.tex"
with open(fn, 'r') as f:
    lines = f.readlines()

for i in range(560, min(630, len(lines))):
    print(f"{i+1}:{lines[i].rstrip()}")
