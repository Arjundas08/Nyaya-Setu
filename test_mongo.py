import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load variables from .env
load_dotenv()
uri = os.getenv("MONGO_URI")

if not uri:
    print("❌ Error: MONGO_URI is missing from .env file!")
    exit()

# Hide password for printing
safe_uri = uri.split('@')[-1] if '@' in uri else uri
print(f"🔄 Attempting to connect to: {safe_uri}")

try:
    # 5-second timeout so we don't wait forever
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ SUCCESS! Connected to MongoDB Atlas.")
except Exception as e:
    print("\n❌ CONNECTION FAILED. Reason:")
    print(e)