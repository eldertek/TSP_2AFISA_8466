import cv2
import numpy as np
from django.shortcuts import render

from indexing.faces import detect_faces


def index(request):
    if request.method == "POST":
        photo = request.FILES.get("photo").read()
        photo = np.frombuffer(photo, np.uint8)
        photo = cv2.imdecode(photo, cv2.IMREAD_COLOR)

        detected_faces = detect_faces(photo)
        return render(
            request, "indexing/index.html", {"detected_faces": detected_faces}
        )
    return render(request, "indexing/index.html")
