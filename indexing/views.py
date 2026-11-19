from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from indexing.models import Photo
from indexing.tasks import index_photo

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MiB
ALLOWED_IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".webp"})


def _validate_uploaded_photo(uploaded_file) -> str | None:
    if uploaded_file is None:
        return "No photo file provided."
    ext = Path(getattr(uploaded_file, "name", "") or "").suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return "Unsupported image format (jpg, jpeg, png, webp allowed)."
    content_type = (getattr(uploaded_file, "content_type", "") or "").lower()
    if content_type and not content_type.startswith("image/"):
        return "Invalid MIME type for uploaded photo."
    size = getattr(uploaded_file, "size", None)
    if size is not None and size > MAX_UPLOAD_BYTES:
        return "Uploaded photo exceeds the 10 MiB limit."
    return None


@login_required
def index(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("photo")
        error = _validate_uploaded_photo(uploaded_file)
        if error:
            return render(request, "indexing/index.html", {"error": error}, status=400)
        uploaded_file.seek(0)

        photo_obj = Photo.objects.create(image=uploaded_file, uploaded_by=request.user)

        index_photo.apply_async(args=[photo_obj.id], queue="indexing")

        return render(
            request,
            "indexing/index.html",
            {"message": "Photo uploaded and indexing started."},
        )
    return render(request, "indexing/index.html")
