from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext as _

from indexing.models import Album, Photo
from indexing.tasks import index_photo


@login_required
def index(request):
    if not request.user.is_staff:
        raise PermissionDenied("You do not have permission to access this page.")

    albums = Album.objects.order_by("-event_date")

    if request.method == "POST":
        album_id = request.POST.get("album_id")
        album_name = request.POST.get("album_name", "").strip()
        event_date_str = request.POST.get("event_date")

        album = None

        if album_name and event_date_str:
            try:
                event_date = parse_datetime(event_date_str)
                if event_date is None:
                    raise ValueError(_("Invalid date format."))
                if timezone.is_naive(event_date):
                    event_date = timezone.make_aware(
                        event_date, timezone.get_current_timezone()
                    )
                album, created = Album.objects.get_or_create(
                    name=album_name, event_date=event_date
                )
            except ValueError as e:
                return render(
                    request,
                    "indexing/index.html",
                    {"albums": albums, "error": str(e)},
                )
        elif album_id:
            try:
                album = Album.objects.get(id=album_id)
            except Album.DoesNotExist:
                return render(
                    request,
                    "indexing/index.html",
                    {"albums": albums, "error": _("Selected album does not exist.")},
                )

        uploaded_files = request.FILES.getlist("photos")

        for uploaded_file in uploaded_files:
            photo_obj = Photo.objects.create(
                image=uploaded_file, album=album, uploaded_by=request.user
            )
            index_photo.apply_async(args=[photo_obj.id], queue="indexing")

        albums = Album.objects.order_by("-event_date")

        return render(
            request,
            "indexing/index.html",
            {
                "message": _("%(count)d photos uploaded and queued for indexing.")
                % {"count": len(uploaded_files)},
                "albums": albums,
            },
        )
    return render(request, "indexing/index.html", {"albums": albums})
