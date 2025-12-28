import matplotlib.pyplot as plt
import numpy as np
import os

# --- 1. Define Data ---
# angles_deg = np.array([56.332, 63.324, 60.326, 56.33, 63.326, 60.332])
angles_deg = np.array([55.998, 57.995, 65.991, 55.998, 57.994, 65.99])

N = len(angles_deg)
roman_labels = ['I', 'II', 'III', 'IV', 'V', 'VI']

# --- 2. Setup Geometry ---
widths_rad = np.deg2rad(angles_deg)
starts_rad = np.concatenate(([0], np.cumsum(widths_rad)[:-1]))
fixed_radius = 10.0

# --- 3. Professional Grayscale Colors ---
# Light Grey -> Medium Grey -> Dark Grey (Repeats twice)
gray_palette = ['#F0F0F0', '#BDBDBD', '#525252'] * 2 

# --- 4. Create Plot ---
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})

# Plot wedges
bars = ax.bar(x=starts_rad, height=fixed_radius, width=widths_rad, 
              bottom=0.0, align='edge', color=gray_palette, edgecolor='white', linewidth=2)

# --- 5. Labels & Customization ---
for start_angle, width_angle, val_deg, roman, bg_color in zip(starts_rad, widths_rad, angles_deg, roman_labels, gray_palette):
    
    center_angle = start_angle + (width_angle / 2)
    
    # Determine Text Contrast (Dark text for light bg, White text for dark bg)
    h = bg_color.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
    main_text_color = 'black' if brightness > 125 else 'white'
    
    # A. Roman Numeral (Header)
    ax.text(center_angle, 7.5, roman,
            ha='center', va='center', fontsize=24, fontweight='bold',
            color=main_text_color, alpha=0.4)

    # B. Angle Value (Data)
    ax.text(center_angle, 4.5, f"{val_deg:.3f}°", 
            ha='center', va='center', fontsize=14, fontweight='bold', 
            color=main_text_color, rotation=0)

# --- 6. Clean Up ---
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.grid(False)
ax.spines['polar'].set_visible(False)

# Update Title
plt.title("LUT angle", va='bottom', fontsize=16, fontweight='bold', y=1.02, color='#333333')

plt.tight_layout()

# --- 7. Save to Folder ---
output_folder = 'figures'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Save as PNG with high DPI (300) for professional quality
save_path = os.path.join(output_folder, 'lut_angle_chart.png')
plt.savefig(save_path, dpi=300, bbox_inches='tight')
print(f"Figure saved successfully to: {save_path}")

plt.show()