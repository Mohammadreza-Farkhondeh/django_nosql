from django.shortcuts import render
from django.http import HttpResponse
from persian_wordcloud.wordcloud import PersianWordCloud

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
        data = process_uploaded_file(uploaded_file)

        save_option = request.POST.get('save_option', 'mongodb')  # default is mongodb
        request.session['db_type'] = save_option

        write_to_database(data, save_option)

        return HttpResponse("File uploaded successfully!")

    return render(request, 'upload_file.html')


def crud_page(request):
    """
    shows a table with CRUD operations on the uploaded file data
    db_type from "db_type" in request.session
    get fields from first row of data
    """
    db_type = request.session.get('db_type')

    if db_type not in ['mongodb', 'elasticsearch']:
        return HttpResponse("Invalid database type")

    data = get_data_from_database(db_type)
    fields = list(data[0].keys())

    # Handle search query
    query = request.GET.get('q', '').strip()
    if query:
        data = perform_search(query, data)

    if request.method == 'POST':
        if 'create' in request.POST:
            data = get_data_from_database(db_type)
            new_row = {}  # Dictionary to store the new row data

            # Iterate over the fields and get the new values from the form
            for field in fields:
                new_row[field] = request.POST.get(field, '')

            data.append(new_row)
            save_to_database(data, db_type)

        elif 'update' in request.POST:
            row_id = int(request.POST.get('row_id'))
            updated_row = {}  # Dictionary to store the updated row data

            # Iterate over the fields and get the updated values from the form
            for field in fields:
                updated_row[field] = request.POST.get(field, '')

            data[row_id] = updated_row
            save_to_database(data, db_type)

        elif 'delete' in request.POST:
            row_id = int(request.POST.get('row_id'))

            data.pop(row_id)

            save_to_database(data, db_type)

    fields = list(data[0].keys())

    return render(request, 'crud_page.html', {'data': data, 'fields': fields, 'db_type': db_type})


def wordcloud_page(request):
    """
    Shows a wordcloud of the uploaded file data
    db_type from "db_type" in request.session
    """
    db_type = request.session.get('db_type')
    if db_type not in ['mongodb', 'elasticsearch']:
        return HttpResponse("Invalid database type")

    data = get_data_from_database(db_type)

    wordcloud_data = {}
    for field in data[0].keys():
        values = [row[field] for row in data if field in row]
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
