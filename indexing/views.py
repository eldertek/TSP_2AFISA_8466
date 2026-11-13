import cv2
import numpy as np
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from indexing.faces import detect_faces, extract_embedding
from indexing.models import Face, Photo


@login_required
def index(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("photo")
        image_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        photo = np.frombuffer(image_bytes, np.uint8)
        photo = cv2.imdecode(photo, cv2.IMREAD_COLOR)

        detected_faces = detect_faces(photo)

        photo_obj = Photo.objects.create(image=uploaded_file, uploaded_by=request.user)

        for face in detected_faces:
            embedding = extract_embedding(photo, face)
            (
                Face.objects.create(
                    photo=photo_obj,
                    embedding=embedding,
                    box_x=int(face[0]),
                    box_y=int(face[1]),
                    box_w=int(face[2]),
                    box_h=int(face[3]),
                )
                if photo_obj
                else None
            )

        return render(
            request, "indexing/index.html", {"detected_faces": detected_faces}
        )
    return render(request, "indexing/index.html")
