import pymongo
from elasticsearch_dsl import connections
from elasticsearch import Elasticsearch

ELASTICSEARCH_CONNECTIONS = {
    'default': {
        'hosts': 'elasticsearch',
        'port': 9200,
    },
}
MONGO_CONNECTION_STRING = "mongodb://mongodb:27017"

# Establish MongoDB connection
mongo_client = pymongo.MongoClient(MONGO_CONNECTION_STRING)
mongo_db = mongo_client.database
mongo_collection = mongo_db.collection

# Establish Elasticsearch connection
connections.configure(**ELASTICSEARCH_CONNECTIONS)
es = connections.get_connection(alias='default')
print(type(es))