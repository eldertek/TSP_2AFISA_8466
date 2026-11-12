from django.contrib import admin

from .models import Album, Face, Person, Photo

admin.site.register(Album)
admin.site.register(Photo)
admin.site.register(Person)
admin.site.register(Face)
