import io

from celery import shared_task
from django.contrib.auth import get_user_model

from search.service import research


@shared_task
def search_faces_task(image_hex, user_id=None):
    photo_file = io.BytesIO(bytes.fromhex(image_hex))
    user = None
    if user_id is not None:
        User = get_user_model()
        user = User.objects.filter(id=user_id).first()
    return research(photo_file, user=user)
