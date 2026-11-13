from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

TSP_DOMAIN = "@telecom-sudparis.eu"
IMT_DOMAIN = "@imt-bs.eu"


class SchoolEmailUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Adresse mail académique"

    def clean_username(self):
        value = super().clean_username()
        if not value.endswith(TSP_DOMAIN) and not value.endswith(IMT_DOMAIN):
            raise ValidationError(
                "L'adresse mail rentrée doit être l'adresse mail académique."
            )

        return value
