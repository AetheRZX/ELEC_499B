
with open(r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\latex\IEEE-conference-template-062824.tex", 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "Detailed Machine Simulations" in line or "section{" in line or "subsection{" in line:
            print(f"{i+1}: {line.strip()}")
