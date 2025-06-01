import re
import sys

README_PATH = "README.md"

with open(README_PATH, encoding="utf-8") as f:
    content = f.read()

# Count all checkboxes
all_boxes = re.findall(r"- \[.\]", content)
done_boxes = re.findall(r"- \[x\]", content, re.IGNORECASE)

if not all_boxes:
    print("No checkboxes found.")
    sys.exit(0)

total = len(all_boxes)
done = len(done_boxes)
percent = (done / total) * 100

# Optionally, update the README with the new progress
import re

def update_progress_field(field, percent):
    return re.sub(rf"({field}:) \[.*?\]% Complete", rf"\1 [{percent:.0f}]% Complete", content)

content = update_progress_field("Month 1 Progress", percent)
content = update_progress_field("Month 2 Progress", percent)
content = update_progress_field("Month 3 Progress", percent)
content = update_progress_field("Munga \(AI/Analytics\)", percent)
content = update_progress_field("Muchamo \(Payments\)", percent)
content = update_progress_field("Biggie \(Frontend/Invoices\)", percent)
content = update_progress_field("Kevo \(Infrastructure\)", percent)

with open(README_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Progress: {done}/{total} ({percent:.1f}%) complete. Fields updated in README.")
