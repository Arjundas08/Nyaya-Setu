import os

files_to_check = [
    "backend/services/privacy.py",
    "backend/routes/analyze.py",
    "backend/routes/chat.py",
    "backend/routes/search.py",
    "backend/routes/generate.py",
    "backend/routes/predict.py",
    "backend/routes/dashboard.py",
]

for path in files_to_check:
    print(f"\n{'='*60}")
    print(f"FILE: {path}")
    print('='*60)
    if os.path.exists(path):
        # Added encoding="utf-8" here
        with open(path, encoding="utf-8") as f:
            content = f.read()
            print(content)
    else:
        print("❌ FILE DOES NOT EXIST")