import pymongo
from elasticsearch_dsl import connections


# Establish MongoDB connection
mongo_client = pymongo.MongoClient("localhost", 27017)
mongo_db = mongo_client.database
mongo_collection = mongo_db.collection

# Establish Elasticsearch connection
connections.create_connection(alias='default', hosts=['localhost'], timeout=60)
es = connections.get_connection(alias='default')
