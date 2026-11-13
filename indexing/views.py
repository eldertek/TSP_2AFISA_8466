from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from indexing.faces import detect_faces
from indexing.models import Photo
from indexing.tasks import index_photo


@login_required
def index(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("photo")
        uploaded_file.seek(0)

        photo_obj = Photo.objects.create(image=uploaded_file, uploaded_by=request.user)

        index_photo.apply_async(args=[photo_obj.id], queue="indexing")

        return render(
            request,
            "indexing/index.html",
            {"message": "Photo uploaded and indexing started."},
        )
    return render(request, "indexing/index.html")
