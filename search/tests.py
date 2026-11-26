import io
import json
import shutil
import tempfile
import zipfile

import cv2
from channels.auth import AuthMiddlewareStack
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import FileResponse
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.views.defaults import server_error

from indexing.faces import detect_faces, extract_embedding
from indexing.models import Album, Face, Person, Photo
from search.consumers import NotificationConsumer
from search.forms import SchoolEmailUserCreationForm
from search.routing import NotificationConsumer
from search.service import research


class SearchAndRemovalTest(TestCase):
    def setUp(self):
        self.temp_media = tempfile.mkdtemp()
        self.user = get_user_model().objects.create_user(
            username="armstrong@telecom-sudparis.eu",
            password="Password123!",
            is_staff=True,
        )

        album = Album.objects.create(name="Apollo 11", event_date=timezone.now())

        with override_settings(MEDIA_ROOT=self.temp_media):
            for path in (
                "tests/donnees/album/armstrong-portrait.jpg",
                "tests/donnees/album/aldrin-portrait.jpg",
            ):
                with open(path, "rb") as image_file:
                    uploaded = SimpleUploadedFile(
                        path.rsplit("/", 1)[-1],
                        image_file.read(),
                        content_type="image/jpeg",
                    )

                photo_obj = Photo.objects.create(
                    image=uploaded, album=album, uploaded_by=self.user
                )
                image = cv2.imread(path)

                for face in detect_faces(image):
                    indexed_face = Face.objects.create(
                        photo=photo_obj,
                        embedding=extract_embedding(image, face),
                        box_x=int(face[0]),
                        box_y=int(face[1]),
                        box_w=int(face[2]),
                        box_h=int(face[3]),
                    )
                    if "armstrong" in path:
                        self.face = indexed_face

    def test_research_finds_matching_person_and_links_user(self):
        with open("tests/donnees/recherche-armstrong.jpg", "rb") as query_photo:
            results = research(query_photo, user=self.user)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["event"], "Apollo 11")
        self.assertEqual(results[0]["score"] >= 0.363, True)
        self.assertEqual(Face.objects.filter(person__user=self.user).count(), 1)

    def test_remove_from_index_deletes_faces_but_keeps_photos(self):
        with open("tests/donnees/recherche-armstrong.jpg", "rb") as query_photo:
            results = research(query_photo, user=self.user)
        self.client.force_login(self.user)
        response = self.client.post(reverse("remove_from_index"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Person.objects.filter(user=self.user).count(), 0)
        self.assertEqual(Face.objects.count(), 1)
        self.assertEqual(Photo.objects.count(), 2)

    def test_download_archive_only_includes_user_photos(self):
        with open("tests/donnees/recherche-armstrong.jpg", "rb") as query_photo:
            results = research(query_photo, user=self.user)
        self.client.force_login(self.user)
        with override_settings(MEDIA_ROOT=self.temp_media):
            all_photo_ids = list(Photo.objects.values_list("id", flat=True))

            response = self.client.post(
                reverse("download_archive"),
                {"photo_ids": all_photo_ids},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertEqual(
            response["Content-Disposition"],
            'attachment; filename="photos.zip"',
        )
        assert isinstance(response, FileResponse)

        zip_bytes = response.getvalue()
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
            self.assertEqual(len(archive.namelist()), 1)
            self.assertIn("armstrong", archive.namelist()[0])

    def tearDown(self):
        shutil.rmtree(self.temp_media, ignore_errors=True)


class InscriptionFormTest(TestCase):
    def test_academic_email_validation(self):
        form = SchoolEmailUserCreationForm(
            data={
                "username": "test@telecom-sudparis.eu",
                "password1": "MdpTest123!!",
                "password2": "MdpTest123!!",
            }
        )
        self.assertTrue(form.is_valid())

    def test_non_academic_email_validation(self):
        form = SchoolEmailUserCreationForm(
            data={
                "username": "test@gmail.com",
                "password1": "MdpTest123!!",
                "password2": "MdpTest123!!",
            }
        )
        self.assertFalse(form.is_valid())


class ErrorPagesTest(TestCase):
    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
    def test_403_uses_custom_template(self):
        self.client.force_login(
            get_user_model().objects.create_user(
                username="user", password="Password123!", is_staff=False
            )
        )
        response = self.client.get(reverse("indexing:index"))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403.html")

    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
    def test_404_uses_custom_template(self):
        response = self.client.get("/nonexistent-page/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
    def test_500_uses_custom_template(self):
        request = RequestFactory().get("/")
        response = server_error(request)
        self.assertEqual(response.status_code, 500)
        self.assertContains(
            response, b"An internal server error occurred.", status_code=500
        )


class NotificationConsumerTest(TestCase):
    async def test_anonymous_websocket_rejected(self):
        communicator = WebsocketCommunicator(
            AuthMiddlewareStack(NotificationConsumer.as_asgi()),
            "/ws/notifications/",
        )
        connected, _ = await communicator.connect()

        self.assertFalse(connected)

    async def test_authenticated_user_receives_notification(self):
        user = await get_user_model().objects.acreate(
            username="notif@telecom-sudparis.eu"
        )
        await self.client.aforce_login(user)
        session_key = self.client.cookies["sessionid"].value
        communicator = WebsocketCommunicator(
            AuthMiddlewareStack(NotificationConsumer.as_asgi()),
            "/ws/notifications/",
            headers=[(b"cookie", f"sessionid={session_key}".encode())],
        )
        connected, _ = await communicator.connect()

        self.assertTrue(connected)

        channel_layer = get_channel_layer()

        assert channel_layer is not None

        await channel_layer.group_send(
            f"user_{user.pk}", {"type": "notify", "message": "New photo in Gala!"}
        )

        response = await communicator.receive_from(timeout=5)

        self.assertEqual(json.loads(response), {"message": "New photo in Gala!"})

        await communicator.disconnect()
