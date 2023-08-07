from django.db import models


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    db_type = models.CharField(max_length=20)