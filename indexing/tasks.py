import cv2
from celery import shared_task

from indexing.models import Face, Photo
from search.service import detect_faces, extract_embedding


@shared_task
def index_photo(photo_id):
    photo_obj = Photo.objects.get(id=photo_id)
    image = cv2.imread(photo_obj.image.path)
    detected_faces = detect_faces(image)

    for face in detected_faces:
        embedding = extract_embedding(image, face)
        Face.objects.create(
            photo=photo_obj,
            embedding=embedding,
            box_x=int(face[0]),
            box_y=int(face[1]),
            box_w=int(face[2]),
            box_h=int(face[3]),
        )
