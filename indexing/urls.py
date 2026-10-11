from django.urls import path

from . import views

app_name = "indexing"

urlpatterns = [
    path("", views.index, name="index"),
]
