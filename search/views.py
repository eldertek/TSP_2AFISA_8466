from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from indexing.models import Person
from search.forms import SchoolEmailUserCreationForm
from search.tasks import search_faces_task

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MiB
ALLOWED_IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".webp"})


def _validate_search_photo(photo) -> str | None:
    if photo is None:
        return "No photo file provided."
    ext = Path(getattr(photo, "name", "") or "").suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return "Unsupported image format (jpg, jpeg, png, webp allowed)."
    content_type = (getattr(photo, "content_type", "") or "").lower()
    if content_type and not content_type.startswith("image/"):
        return "Invalid MIME type for uploaded photo."
    size = getattr(photo, "size", None)
    if size is not None and size > MAX_UPLOAD_BYTES:
        return "Uploaded photo exceeds the 10 MiB limit."
    return None


@login_required
def home(request):
    if request.method == "POST":
        photo = request.FILES.get("photo")
        error = _validate_search_photo(photo)
        if error:
            return render(request, "search/home.html", {"error": error}, status=400)
        raw = photo.read(MAX_UPLOAD_BYTES + 1)
        if len(raw) > MAX_UPLOAD_BYTES:
            return render(
                request,
                "search/home.html",
                {"error": "Uploaded photo exceeds the 10 MiB limit."},
                status=400,
            )
        task = search_faces_task.apply_async(
            args=[raw.hex(), request.user.id],
            queue="search",
        )
        results = task.get(timeout=30)
        return render(request, "search/home.html", {"results": results})
    return render(request, "search/home.html")


def register(request):
    if request.method == "POST":
        form = SchoolEmailUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = SchoolEmailUserCreationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def remove_from_index(request):
    if request.method == "POST":
        Person.objects.filter(user=request.user).delete()
    return redirect("home")
