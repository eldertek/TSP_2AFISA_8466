import cv2
import numpy as np

from indexing.faces import detect_faces, extract_embedding
from indexing.models import Face, Person


def research(photo, user=None):
    """
    Search for similar faces in the database based on the provided photo.

    @param photo: The uploaded photo file.
    """

    image_bytes = photo.read()
    img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)

    detected_faces = detect_faces(img)

    results = []

    if len(detected_faces) == 0:
        return results
    else:
        query_bytes = extract_embedding(img, detected_faces[0])
        query_embedding = np.frombuffer(query_bytes, dtype=np.float32).reshape(1, -1)
        faces = Face.objects.select_related("photo", "photo__album").all()

        recognizer = cv2.FaceRecognizerSF.create(
            "models/face_recognition_sface_2021dec.onnx", ""
        )

        person = None
        if user and user.is_authenticated:
            person, _ = Person.objects.get_or_create(
                user=user, defaults={"name": user.username}
            )

        for face in faces:
            db_embedding = np.frombuffer(face.embedding, dtype=np.float32).reshape(
                1, -1
            )
            score = recognizer.match(
                query_embedding, db_embedding, cv2.FaceRecognizerSF_FR_COSINE
            )
            if score >= 0.363:
                if person and face.person_id != person.id:
                    face.person = person
                    face.save(update_fields=["person"])
                results.append(
                    {
                        "photo": face.photo.image.url,
                        "event": (
                            face.photo.album.name if face.photo.album else "no-album"
                        ),
                        "date": (
                            face.photo.album.event_date.strftime("%Y-%m-%d")
                            if face.photo.album
                            else face.photo.uploaded_at.strftime("%Y-%m-%d")
                        ),
                        "score": round(float(score), 2),
                    }
                )

        results.sort(key=lambda x: x["score"], reverse=True)
        return results
