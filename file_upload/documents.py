from elasticsearch_dsl import Document, Object, Date


class FileDataDocument(Document):
    data = Object()
    uploaded_at = Date()
