import pymongo
import certifi
import urllib
import json

class Mongo_connection():
    def __init__(self):
        with open("mongo_config.json") as f:
            config = json.load(f)

        username = config["username"]
        password = config["password"]

        self.client = pymongo.MongoClient("mongodb+srv://" + username + ":" + urllib.parse.quote(password) + "@cluster0.8tzvt.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",tlsCAFile=certifi.where())
        
        self.db = self.client['eye_tracking_db']
        self.collection = self.db['fixation_sequences']
        print("[INFO] Created a mongodb instance.")

    def connect(self):
        x = self.collection.count()
        print("[INFO] Currently connected to eye_tracking_db/fixation_sequences.")
        print("[INFO] Found {} documents.".format(x))

    def insert(self, document):
        x = self.collection.insert_one(document)
        print("[INFO] insert status: ", x.acknowledged)

    def delete_all(self):
        x = self.collection.delete_many({})
        print("[INFO] delete status: ", x.acknowledged)

    def find_all(self):
        x = self.collection.find({})
        return(x)

    def find_one(self, query):
        x = self.collection.find_one(query)
        return(x)

    def find(self, query):
        x = self.collection.find(query)
        return(x)

if __name__=="__main__":
    mongo = Mongo_connection()
    mongo.connect()


    