from django.contrib import admin

from .models import Album, Face, Person, Photo


class AlbumAdmin(admin.ModelAdmin):
    list_display = ("name", "event_date", "published_date")


class PhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "album", "uploaded_by", "uploaded_at")
    list_select_related = ("album", "uploaded_by")


class PersonAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "created_at")
    list_select_related = ("user",)


class FaceAdmin(admin.ModelAdmin):
    list_display = ("id", "photo", "person", "box_x", "box_y")
    list_select_related = ("photo", "photo__album", "person")
