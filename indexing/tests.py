import shutil
import tempfile
from unittest.mock import patch

import cv2
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from indexing.faces import detect_faces, extract_embedding
from indexing.models import Album, Photo


class FaceRecognitionTest(TestCase):
    def test_detect_faces_and_extract_embedding(self):
        image = cv2.imread("tests/donnees/album/equipage-apollo-11.jpg")

        faces = detect_faces(image)

        self.assertEqual(len(faces), 3, "Expected 3 faces to be detected in the image.")

        embedding = extract_embedding(image, faces[0])

        self.assertEqual(len(embedding), 512, "Expected embedding length to be 512.")


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
