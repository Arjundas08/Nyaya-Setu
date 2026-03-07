import os, sys

print("=" * 60)
print("  FOLDER STRUCTURE CHECK")
print("=" * 60)

# Show top-level structure
root = os.getcwd()
print(f"\nYou are in: {root}\n")

for item in sorted(os.listdir(root)):
    full = os.path.join(root, item)
    if os.path.isdir(full):
        print(f"  📁 {item}/")
        try:
            for sub in sorted(os.listdir(full)):
                subfull = os.path.join(full, sub)
                if os.path.isdir(subfull):
                    print(f"       📁 {sub}/")
                    try:
                        for subsub in sorted(os.listdir(subfull)):
                            print(f"            📄 {subsub}")
                    except: pass
                else:
                    print(f"       📄 {sub}")
        except: pass
    else:
        print(f"  📄 {item}")

# Print main.py contents wherever it is
print("\n" + "=" * 60)
print("  CURRENT main.py CONTENTS")
print("=" * 60)

found = False
for path in ["main.py", "backend/main.py", "app/main.py"]:
    if os.path.exists(path):
        print(f"\nFound at: {path}\n")
        with open(path) as f:
            print(f.read())
        found = True
        break

if not found:
    print("❌ Could not find main.py in expected locations!")
    for dirpath, dirs, files in os.walk("."):
        for f in files:
            if f == "main.py":
                print(f"  Found at: {os.path.join(dirpath, f)}")