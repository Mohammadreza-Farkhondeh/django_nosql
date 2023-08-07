import csv
import json
from datetime import datetime
from db import mg, es
from elasticsearch_dsl import Search, Index
from .documents import FileDataDocument


def process_uploaded_file(file):
    """
    return a list of dictionary from rows in data wheter its csv or json file
    """
    data = []
    content_type = file.content_type

    if content_type == 'text/csv':
        with file:
            reader = csv.DictReader(file.read().decode('unicode-escape').splitlines())
            data = [row for row in reader]

    elif content_type == 'application/json':
        with file:
            data = json.load(file)

    return data


def write_to_database(data, id, db_type):
    """
    get a list of dictionaries, then save them each in elasticsearch
    """
    index_name = f'file_{id}'
    if db_type == 'elasticsearch':
        FileDataDocument.init(index=index_name)
        # FileDataDocument._doc_type.mapping.meta('_id', enabled=True)

        for row in data:
            FileDataDocument(data=row, uploaded_at=datetime.now()).save(index=index_name)

    elif db_type == 'mongodb':
        cl = mg[index_name]
        cl.insert_many([{'data': row, 'uploaded_at': datetime.now()} for row in data])


def get_data_from_database(file_id, db_type):
    """
    retrieve list of rows from the database
    """
    index_name = f'file_{file_id}'

    if db_type == 'mongodb':
        cl = mg[index_name]
        data = list(cl.find())
    elif db_type == 'elasticsearch':
        s = FileDataDocument.search()
        data = [hit.to_dict() for hit in s.execute()]

    return data


def save_to_database(data, file_id, db_type):
    """
    save a list of dictionaries to the database
    """
    index_name = f'file_{file_id}'
    if db_type == 'elasticsearch':
        index = Index(index_name)
        index.delete()
        for row in data:
            FileDataDocument(data=row, uploaded_at=datetime.now()).save(index=index_name)

    elif db_type == 'mongodb':
        cl = mg[index_name]
        cl.delete_many({})
        cl.insert_many([{'data': row['data'], 'uploaded_at': datetime.now()} for row in data])


def perform_search(query, file_id, db_type):
    """
    performs searching a query against database
    return a list of dictionaries as get_data_from_database()
    """
    index_name = f'file_{file_id}'
    data = []

    if db_type == 'elasticsearch':

        s = Search(using=es)
        s = s.query("query_string", query=query)
        response = s.execute()
        hits = response['hits']['hits']
        data = [hit.to_dict()['_source'] for hit in hits]

    elif db_type == 'mongodb':
        cl = mg[index_name]
        regex = f".*{query}.*"
        mongo_query = {"data": {"$regex": regex, "$options": "i"}}
        result = cl.find(mongo_query)
        # Convert MongoDB cursor to a list
        data = list(result)

    return data
