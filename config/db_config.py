from pymongo import MongoClient

MONGO_URI = "mongodb+srv://Nishant111:oIhou7dydFdqioxi@cluster0.wjru3wh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "test"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
