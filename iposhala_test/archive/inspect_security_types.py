from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["iposhala"]
collection = db["ipo_past_master"]

types = collection.distinct("security_type")
print("Distinct Security Types:", types)

# Also check a few docs to see if the field name is correct
print("\nSample Docs:")
for doc in collection.find().limit(5):
    print(doc.get("symbol"), doc.get("security_type"))
