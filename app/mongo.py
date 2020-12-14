import pymongo
import typing
import random
import ast
import pydantic
from bson.objectid import ObjectId

class Database:

    def __init__(self):
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = self.client.textbase
        self.objects_collection = self.db.texts
    
    def find_document(self,collection, elements, multiple=True):
        if multiple:
            results = collection.find(elements)
            return [r for r in results]
        else:
            return collection.find_one(elements)


    def insert_document(self,collection, data):
        return collection.insert_one(data).inserted_id


    def delete_document(self, collection, query):
        collection.delete_one(query)


    def update_document(self,collection, query_elements, new_values):
        collection.update_one(query_elements, {'$set': new_values})


    def printing(self):
        results = self.find_document(self.objects_collection, {})
        return results
