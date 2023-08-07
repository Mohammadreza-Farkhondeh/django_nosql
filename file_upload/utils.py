import csv
import json
import io
from datetime import datetime
from elasticsearch_dsl import Search
from db import mongo_collection, es
from .documents import FileDataDocument


def process_uploaded_file(file, file_extension):
    """
    return a list of dictionary from rows in data wheter its csv or json file
    """
    data = []
    # full of security issues
    if file_extension == 'csv':
        csv_file = io.StringIO(file.read().decode('utf-8'))

        reader = csv.DictReader(csv_file)
        data = [row for row in reader]

    elif file_extension == 'json':
        with open(file, 'r') as jsonfile:
            data = json.load(jsonfile)
    return data


def write_to_database(data, db_type):
    """
    get a list of dictionaries, then save them each in elasticsearch
    """
    if db_type == 'elasticsearch':
        for row in data:
            FileDataDocument(meta={'id': row.get('id', None)}, data=row, uploaded_at=datetime.now()).save(index='filedata')
    elif db_type == 'mongodb':
        mongo_collection.insert_many(data)


def get_data_from_database(db_type):
    """
    retrieve list of rows from the database
    """
    if db_type == 'mongodb':
        # Retrieve data from MongoDB
        data = list(mongo_collection.find())
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
        mongo_collection.delete_many({})  # Clear the existing data
        mongo_collection.insert_many(data)
    else:
        # Save data to Elasticsearch
        for row in data:
            FileDataDocument(meta={'id': row.get('id', None)}, data=row, uploaded_at=datetime.now()).save(index='filedata')


def perform_search(query, db_type):
    """
    performs searching a query against database
    return a list of dictionaries as get_data_from_database()
    """
    print(query)
    data = []
    if db_type == 'elasticsearch':
        s = Search(using=es, index='filedata')
        s = s.query("query_string", query=query)
        # Execute the search query
        response = s.execute()
        print(response)
        data = [hit['_source'] for hit in response.hits]

    elif db_type == 'mongodb':
        mongo_query = {
            "$or": [
                {key: {"$regex": query, "$options": "i"} for key in mongo_collection.find_one().keys()}
            ]
        }

        # Execute the search query
        result = mongo_collection.find(mongo_query)

        # Convert MongoDB cursor to a list
        data = list(result)
    print(data)
    return data
