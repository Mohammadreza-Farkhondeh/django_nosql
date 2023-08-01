from elasticsearch_dsl import Document, Text, Date


class FileDataDocument(Document):
    data = Text()
    uploaded_at = Date()

    class Index:
        name = 'filedata'
