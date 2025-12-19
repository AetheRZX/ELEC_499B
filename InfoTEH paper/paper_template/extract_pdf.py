from pypdf import PdfReader
import os

files = [
    "MarkPhung_BAScThesis_17Apr2025_final.pdf",
    "c6a651b6-cf66-47d3-be07-e093fbeb753a.pdf"
]

for f in files:
    print(f"\n--- Extracting {f} ---")
    if not os.path.exists(f):
        print("File not found.")
        continue
    try:
        reader = PdfReader(f)
        # Extract first 5 pages to get Abstract/Intro/Theory
        for i in range(min(5, len(reader.pages))):
            print(f"\n[Page {i+1}]")
            print(reader.pages[i].extract_text())
    except Exception as e:
        print(f"Error reading {f}: {e}")
