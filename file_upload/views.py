from django.shortcuts import render
from django.http import HttpResponse

from .utils import (process_uploaded_file,
                    save_to_elasticsearch,
                    save_to_mongodb,)


def upload_file(request):
    """
    Upload a file and save it to MongoDB or Elasticsearch
    db_type from "save_option" in request.POST
    saves db_type in request.session
    """
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        data = process_uploaded_file(uploaded_file)

        save_option = request.POST.get('save_option', 'mongodb')  # default is mongodb
        request.session['db_type'] = save_option

        if save_option == 'mongodb':
            save_to_mongodb(data)
        elif save_option == 'elasticsearch':
            save_to_elasticsearch(data)

        return HttpResponse("File uploaded successfully!")

    return render(request, 'upload_file.html')
