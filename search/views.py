import io
import os
import zipfile

from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import redirect, render

from indexing.models import Person, Photo
from search.forms import SchoolEmailUserCreationForm
from search.tasks import search_faces_task


@login_required
def home(request):
    if request.method == "POST":
        photo = request.FILES.get("photo")
        if photo:
            task = search_faces_task.apply_async(
                args=[photo.read().hex(), request.user.id],
                queue="search",
            )
            results = task.get(timeout=30)
            if request.headers.get("HX-Request"):
                return render(request, "search/_results.html", {"results": results})
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


@login_required
def download_archive(request):
    if request.method != "POST":
        return redirect("home")

    photo_ids = request.POST.getlist("photo_ids")
    photos = (
        Photo.objects.filter(id__in=photo_ids, faces__person__user=request.user).all()
        if request.user.is_staff
        else Photo.objects.filter(
            id__in=photo_ids, faces__person__user=request.user
        ).distinct()
    )

    if not photos.exists():
        return redirect("home")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for photo in photos:
            archive.write(
                photo.image.path,
                arcname=f"{photo.id}_{os.path.basename(photo.image.name)}",
            )

    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename="photos.zip",
        content_type="application/zip",
    )
