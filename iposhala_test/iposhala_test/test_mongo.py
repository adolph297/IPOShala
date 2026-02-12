from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')

print("=" * 60)
print("🔍 MongoDB Connection Test")
print("=" * 60)
print(f"📍 MongoDB URI: {MONGO_URI}")
print(f"📊 Database Name: {DB_NAME}")
print("=" * 60)

try:
    # Create MongoDB client
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    
    # Test connection
    client.server_info()
    
    # Get database
    db = client[DB_NAME]
    
    # List collections
    collections = db.list_collection_names()
    
    print("✅ MongoDB connection successful!")
    print(f"\n📁 Collections in '{DB_NAME}' database:")
    if collections:
        for col in collections:
            count = db[col].count_documents({})
            print(f"   - {col}: {count} documents")
    else:
        print("   (No collections yet - database is empty)")
    
    print("\n" + "=" * 60)
    print("✅ All checks passed! MongoDB is ready to use.")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ MongoDB connection failed!")
    print(f"Error: {e}")
    print("\n" + "=" * 60)
    print("💡 Troubleshooting:")
    print("   1. Make sure MongoDB is installed and running")
    print("   2. Check your MONGO_URI in .env file")
    print("   3. For local MongoDB: run 'net start MongoDB'")
    print("   4. For Atlas: verify connection string and IP whitelist")
    print("=" * 60)
