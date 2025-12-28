
fn = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\latex\IEEE-conference-template-062824.tex"
with open(fn, 'r') as f:
    lines = f.readlines()

found = -1
for i, line in enumerate(lines):
    if "Detailed Machine Simulations" in line:
        found = i
        break

if found != -1:
    print(f"Found at line {found+1}")
    for j in range(max(0, found), min(len(lines), found + 100)):
        print(f"{j+1}:{lines[j].rstrip()}")
else:
    print("Not found")
