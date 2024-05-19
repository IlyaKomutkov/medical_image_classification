from django.urls import path, re_path
from . import views

app_name = 'main'
urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    re_path(r'^classification/(?P<lesion_name>.*)$', views.classification, name='classification')
]