from django.conf import settings
from django.db import models


class Album(models.Model):
    name = models.CharField(max_length=100)
    published_date = models.DateTimeField(auto_now_add=True)
    event_date = models.DateTimeField()

    def __str__(self):
        return self.name


class Photo(models.Model):
    album = models.ForeignKey(
        Album, on_delete=models.SET_NULL, null=True, related_name="photos"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_photos",
    )
    image = models.ImageField(upload_to="photos/")

    def __str__(self):
        return f"Photo uploaded by {self.uploaded_by} on {self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}"
