from django.shortcuts import render

from recherche.service import rechercher

# Create your views here.


def accueil(request):
    if request.method == "POST":
        photo = request.FILES.get("photo")
        if photo:
            resultats = rechercher(photo)
            return render(request, "recherche/accueil.html", {"resultats": resultats})
    return render(request, "recherche/accueil.html")
