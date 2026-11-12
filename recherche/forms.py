from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

ADRESSE_TSP = "@telecom-sudparis.eu"
ADRESSE_IMT = "@imt-bs.eu"


class CreationCompteAvecMail(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Adresse mail académique"

    def clean_username(self):
        valeur = super().clean_username()
        if not valeur.endswith(ADRESSE_TSP) and not valeur.endswith(ADRESSE_IMT):
            raise ValidationError(
                "L'adresse mail rentrée doit être l'adresse mail académique."
            )

        return valeur
