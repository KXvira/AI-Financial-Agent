#!/usr/bin/env python3
import re
import os

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
README_PATH = os.path.join(PROJECT_ROOT, "README.md")

try:
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Count all checkboxes
    all_boxes = re.findall(r"- \[.\]", content)
    done_boxes = re.findall(r"- \[x\]", content, re.IGNORECASE)
    
    total = len(all_boxes)
    done = len(done_boxes)
    
    if total == 0:
        print("No checkboxes found in README.")
    else:
        percent = (done / total) * 100
        print(f"Project Progress: {done}/{total} tasks completed ({percent:.1f}%)")
        
        # List areas with progress
        areas = [
            "Month 1 Progress", 
            "Month 2 Progress", 
            "Month 3 Progress",
            "Munga (AI/Analytics)",
            "Muchamo (Payments)",
            "Biggie (Frontend/Invoices)",
            "Kevo (Infrastructure)"
        ]
        
        for area in areas:
            print(f"{area}: {percent:.0f}% Complete")
except Exception as e:
    print(f"Error processing README: {e}")
