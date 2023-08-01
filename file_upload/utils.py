import csv
import json
import datetime
from db import mongo_db
from .documents import FileDataDocument


def process_uploaded_file(uploaded_file):
    """
    return a list of dictionery from rows in data wheter its csv or json file
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
    get a list of dictioneries, then save them each in mongodb
    """
    collection = mongo_db.collection
    collection.insert_many(data)


def save_to_elasticsearch(data):
    """
    get a list of dictioneries, then save them each in elasticsearch
    """
    for row in data:
        FileDataDocument(meta={'id': row.get('id', None)}, data=row, uploaded_at=datetime.now()).save(index='filedata')
