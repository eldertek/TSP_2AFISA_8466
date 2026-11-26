import cv2
from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

from indexing.faces import assign_person, detect_faces, extract_embedding
from indexing.models import Face, Photo


@shared_task
def index_photo(photo_id):
    photo_obj = Photo.objects.get(id=photo_id)
    image = cv2.imread(photo_obj.image.path)
    detected_faces = detect_faces(image)

    for face in detected_faces:
        embedding = extract_embedding(image, face)
        person = assign_person(embedding)

        Face.objects.create(
            person=person,
            photo=photo_obj,
            embedding=embedding,
            box_x=int(face[0]),
            box_y=int(face[1]),
            box_w=int(face[2]),
            box_h=int(face[3]),
        )

        if person.user_id is not None:
            channel_layer = get_channel_layer()
            if channel_layer is not None:
                album = getattr(photo_obj, "album", None)
                album_name = album.name if album else "No album"
                async_to_sync(channel_layer.group_send)(
                    f"user_{person.user_id}",
                    {
                        "type": "notify",
                        "message": f"A new photo of you has been published in {album_name}.",
                    },
                )
