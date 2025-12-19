import matplotlib.pyplot as plt

def create_placeholder(text, filename):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.text(0.5, 0.5, text, fontsize=20, ha='center', va='center', bbox=dict(boxstyle="round", fc="w"))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("PLACEHOLDER")
    plt.savefig(filename, bbox_inches='tight')
    plt.close()

create_placeholder("Flowchart Placeholder\n(See TikZ code)", "latex/figures/flowchart_placeholder.png")
create_placeholder("Speed Step Response\n(Placeholder)", "latex/figures/speed_step_placeholder.png")
create_placeholder("Torque Step Response\n(Placeholder)", "latex/figures/torque_step_placeholder.png")
