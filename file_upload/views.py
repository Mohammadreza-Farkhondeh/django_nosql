from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from persian_wordcloud.wordcloud import PersianWordCloud

from .models import UploadedFile
from .utils import (process_uploaded_file,
                    write_to_database,
                    save_to_database,
                    get_data_from_database,
                    perform_search)


def upload_file(request):
    """
    Upload a file and save it to MongoDB or Elasticsearch
    db_type from "save_option" in request.POST
    saves db_type in request.session
    """
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        save_option = request.POST.get('save_option', 'mongodb')  # default is mongodb

        uploaded_file_obj = UploadedFile.objects.create(file=uploaded_file, db_type=save_option)

        file_id = uploaded_file_obj.id

        data = process_uploaded_file(uploaded_file)

        write_to_database(data, file_id, save_option)

        return HttpResponse(f'File uploaded successfully!, <a href="crud/{id}">CRUD page</a> and <a href="wordcloud/{id}">WordCloud page</a>' )

    return render(request, 'upload_file.html')


def crud_page(request, id):
    """
    shows a table with CRUD operations on the uploaded file data
    db_type from "db_type" in request.session
    get fields from first row of data
    """
    uploaded_file_instance = get_object_or_404(UploadedFile, pk=id)

    db_type, file_id = uploaded_file_instance.db_type, uploaded_file_instance.id

    if db_type not in ['mongodb', 'elasticsearch']:
        return HttpResponse("Invalid database type")

    data = get_data_from_database(file_id, db_type)
    fields = list(data[0].keys())

    query = request.GET.get('q', '').strip()
    if query:
        data = perform_search(query, file_id, db_type)

    if request.method == 'POST':
        if 'create' in request.POST:
            new_row = {}

            for field in fields:
                new_row[field] = request.POST.get(field, '')

            data.append(new_row)
            save_to_database(data, file_id, db_type)

        elif 'update' in request.POST:
            row_id = int(request.POST.get('row_id'))
            updated_row = {}

            for field in fields:
                updated_row[field] = request.POST.get(field, '')

            data[row_id] = updated_row
            save_to_database(data, file_id, db_type)

        elif 'delete' in request.POST:
            row_id = int(request.POST.get('row_id'))

            data.pop(row_id)

            save_to_database(data, file_id, db_type)

    fields = list(data[0].keys())

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'crud_page.html', {'page_obj': page_obj, 'fields': fields, 'db_type': db_type})


def wordcloud_page(request, id):
    """
    Shows a wordcloud of the uploaded file data
    db_type from "db_type" in request.session
    """
    uploaded_file_instance = get_object_or_404(UploadedFile, pk=id)

    db_type, file_id = uploaded_file_instance.db_type, uploaded_file_instance.id
    
    if db_type not in ['mongodb', 'elasticsearch']:
        return HttpResponse("Invalid database type")

    data = get_data_from_database(file_id, db_type)
    wordcloud_data = {}
    for field in data[0].keys():
        values = [row[field] for row in data if field in row]
        print(values)
        text = ' '.join(values)
        persian_wordcloud = PersianWordCloud(
                            # only_persian=True,
                            max_words=120,
                            margin=10,
                            width=1920,
                            height=1080,
                            min_font_size=1,
                            max_font_size=500,
                            background_color="white",)
        persian_wordcloud.generate(text)

        # Convert the PersianWordCloud instance to an image
        wordcloud_data[field] = persian_wordcloud.to_image()
    return render(request, 'wordcloud_page.html', {'db_type': db_type, 'wordcloud_data': wordcloud_data})
