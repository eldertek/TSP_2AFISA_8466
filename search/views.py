from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from indexing.models import Person
from search.forms import SchoolEmailUserCreationForm
from search.service import research


@login_required
def home(request):
    if request.method == "POST":
        photo = request.FILES.get("photo")
        if photo:
            results = research(photo, user=request.user)
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
