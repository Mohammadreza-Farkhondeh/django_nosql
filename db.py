import pymongo
from elasticsearch_dsl import connections


# Establish MongoDB connection
mongo_client = pymongo.MongoClient("localhost", 27017)
mg = mongo_client.database

# Establish Elasticsearch connection
connections.create_connection(alias='default', hosts=['localhost'], timeout=60)
es = connections.get_connection(alias='default')
