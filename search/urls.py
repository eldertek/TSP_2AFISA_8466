from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("remove/", views.remove_from_index, name="remove_from_index"),
]
