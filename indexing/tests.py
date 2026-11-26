import shutil
import tempfile
from unittest.mock import patch

import cv2
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from indexing.faces import detect_faces, extract_embedding
from indexing.models import Album, Face, Person, Photo
from indexing.tasks import index_photo


class FaceRecognitionTest(TestCase):
    def test_detect_faces_and_extract_embedding(self):
        image = cv2.imread("tests/donnees/album/equipage-apollo-11.jpg")

        faces = detect_faces(image)

        self.assertEqual(len(faces), 3, "Expected 3 faces to be detected in the image.")

        embedding = extract_embedding(image, faces[0])

        self.assertEqual(len(embedding), 512, "Expected embedding length to be 512.")

    def test_detect_faces_on_large_image(self):
        image = cv2.imread("tests/donnees/album/armstrong-portrait.jpg")
        assert image is not None
        height, width = image.shape[:2]
        large_image = cv2.resize(image, (3000, int(height * 3000 / width)))

        faces = detect_faces(large_image)

        self.assertEqual(len(faces), 1)
        self.assertEqual(len(extract_embedding(large_image, faces[0])), 512)


class IndexingViewTest(TestCase):
    def setUp(self):
        self.temp_media = tempfile.mkdtemp()
        User = get_user_model()
        self.student = User.objects.create_user(
            username="student@telecom-sudparis.eu",
            password="Password123!",
            is_staff=False,
        )
        self.admin = User.objects.create_user(
            username="admin_test",
            password="Password123!",
            is_staff=True,
        )
        self.url = reverse("indexing:index")

    def tearDown(self):
        shutil.rmtree(self.temp_media, ignore_errors=True)

    def test_anonymous_redirected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_non_staff_forbidden(self):
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_staff_allowed(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_staff_can_upload_album_photos(self):
        self.client.force_login(self.admin)

        with open("tests/donnees/album/armstrong-portrait.jpg", "rb") as image_file:
            photo1 = SimpleUploadedFile(
                "armstrong-portrait.jpg",
                image_file.read(),
                content_type="image/jpeg",
            )
        with open("tests/donnees/album/aldrin-portrait.jpg", "rb") as image_file:
            photo2 = SimpleUploadedFile(
                "aldrin-portrait.jpg",
                image_file.read(),
                content_type="image/jpeg",
            )

        with override_settings(MEDIA_ROOT=self.temp_media), patch(
            "indexing.views.index_photo.apply_async"
        ) as mock_task:
            response = self.client.post(
                self.url,
                {
                    "album_name": "Apollo 11",
                    "event_date": "2026-11-20T20:00",
                    "photos": [photo1, photo2],
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Album.objects.count(), 1)
        self.assertEqual(Photo.objects.filter(album__name="Apollo 11").count(), 2)
        self.assertEqual(mock_task.call_count, 2)


class PersonClusteringTest(TestCase):
    def setUp(self):
        self.temp_media = tempfile.mkdtemp()
        self.admin = get_user_model().objects.create_user(
            username="admin_test",
            password="Password123!",
            is_staff=True,
        )

    def tearDown(self):
        shutil.rmtree(self.temp_media, ignore_errors=True)

    def test_assign_person_groups_same_person_anonymously(self):

        with override_settings(MEDIA_ROOT=self.temp_media):
            album = Album.objects.create(name="Apollo 11", event_date=timezone.now())

            for path in (
                "tests/donnees/album/aldrin-portrait.jpg",
                "tests/donnees/album/armstrong-portrait.jpg",
                "tests/donnees/album/equipage-apollo-11.jpg",
            ):
                with open(path, "rb") as image_file:
                    uploaded = SimpleUploadedFile(
                        path.rsplit("/", 1)[-1],
                        image_file.read(),
                        content_type="image/jpeg",
                    )

                photo_obj = Photo.objects.create(
                    image=uploaded, album=album, uploaded_by=self.admin
                )
                index_photo(photo_obj.id)

            self.assertEqual(Face.objects.count(), 5)
            self.assertEqual(Person.objects.count(), 3)
            self.assertEqual(Person.objects.filter(name="").count(), 3)
