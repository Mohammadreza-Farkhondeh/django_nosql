import csv
import json
import datetime
from db import mongo_db
from .documents import FileDataDocument


def process_uploaded_file(uploaded_file):
    """
    return a list of dictionary from rows in data wheter its csv or json file
    """
    data = []
    # full of security issues
    if uploaded_file.name.endswith('.csv'):
        with uploaded_file.open() as csvfile:
            reader = csv.DictReader(csvfile)
            data = [row for row in reader]
    elif uploaded_file.name.endswith('.json'):
        with uploaded_file.open() as jsonfile:
            data = json.load(jsonfile)
    return data


def save_to_mongodb(data):
    """
    get a list of dictionaries, then save them each in mongodb
    """
    collection = mongo_db.collection
    collection.insert_many(data)


def save_to_elasticsearch(data):
    """
    get a list of dictionaries, then save them each in elasticsearch
    """
    for row in data:
        FileDataDocument(meta={'id': row.get('id', None)}, data=row, uploaded_at=datetime.now()).save(index='filedata')


def get_data_from_database(db_type):
    """
    retrieve list of rows from the database
    """
    if db_type == 'mongodb':
        # Retrieve data from MongoDB
        collection = mongo_db.collection
        data = list(collection.find())
    else:
        # Retrieve data from Elasticsearch
        s = FileDataDocument.search()
        data = [hit.to_dict() for hit in s.execute()]

    return data


def save_to_database(data, db_type):
    """
    save a list of dictionaries to the database
    """
    if db_type == 'mongodb':
        # Save data to MongoDB
        collection = mongo_db.collection
        collection.delete_many({})  # Clear the existing data
        collection.insert_many(data)
    else:
        # Save data to Elasticsearch
        for row in data:
            FileDataDocument(meta={'id': row.get('id', None)}, data=row, uploaded_at=datetime.now()).save(index='filedata')