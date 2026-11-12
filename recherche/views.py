from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from recherche.forms import CreationCompteAvecMail
from recherche.service import rechercher

# Create your views here.


@login_required
def accueil(request):
    if request.method == "POST":
        photo = request.FILES.get("photo")
        if photo:
            resultats = rechercher(photo)
            return render(request, "recherche/accueil.html", {"resultats": resultats})
    return render(request, "recherche/accueil.html")


def inscription(request):
    if request.method == "POST":
        form = CreationCompteAvecMail(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = CreationCompteAvecMail()
    return render(request, "registration/inscription.html", {"form": form})
