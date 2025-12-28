
fn = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\latex\IEEE-conference-template-062824.tex"
with open(fn, 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if r"\section{Conclusion}" in line:
        print(f"Conclusion found at {i+1}")
        # Print surrounding
        for j in range(max(0, i-5), min(len(lines), i+20)):
            print(f"{j+1}:{lines[j].rstrip()}")
        break
