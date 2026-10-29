"""Print 10 cleaned case names from data files"""
import os

data_dir = "data"
files = sorted([f for f in os.listdir(data_dir) if f.endswith('.txt')])[:10]

print("=" * 80)
print("10 EXTRACTED CASE NAMES")
print("=" * 80)

for i, filename in enumerate(files, 1):
    filepath = os.path.join(data_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        case_name = f.readline().strip()
    print(f"{i}. {case_name}")

print("\n" + "=" * 80)
