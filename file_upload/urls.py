from django.urls import path
from . import views

app_name = 'your_app_name'

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('crud/', views.crud_page, name='crud_page'),
    path('wordcloud/', views.wordcloud_page, name='wordcloud_page'),
]
