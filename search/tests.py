from django.test import TestCase

from recherche.forms import CreationCompteAvecMail

# Create your tests here.


class InscriptionFormTest(TestCase):
    def test_academic_email_validation(self):
        form = CreationCompteAvecMail(
            data={
                "username": "test@telecom-sudparis.eu",
                "password1": "MdpTest123!!",
                "password2": "MdpTest123!!",
            }
        )
        self.assertTrue(form.is_valid())

    def test_non_academic_email_validation(self):
        form = CreationCompteAvecMail(
            data={
                "username": "test@gmail.com",
                "password1": "MdpTest123!!",
                "password2": "MdpTest123!!",
            }
        )
        self.assertFalse(form.is_valid())
