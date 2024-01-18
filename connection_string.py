from pymongo import MongoClient

client = MongoClient("mongodb+srv://aliraza:8K2ow7ADbDJ3Frsp@cluster0.icc31.mongodb.net/?retryWrites=true&w=majority")

db = client['owwlldb']