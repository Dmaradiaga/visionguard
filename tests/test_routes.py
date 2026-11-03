import unittest
from io import BytesIO

from flask import Flask
import numpy as np

from visionguard.app.routes.routes import create_routes


class AllowAll:
    def __init__(self, allowed=True):
        self.allowed = allowed

    def is_allowed(self, _user_id):
        return self.allowed


class FakePhotoService:
    def blur_faces(self, _image_file):
        return np.zeros((8, 8, 3), dtype=np.uint8), 2


class RouteTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["MAX_CONTENT_LENGTH"] = 1024
        self.rate_limiter = AllowAll()
        self.app.register_blueprint(
            create_routes(self.rate_limiter, FakePhotoService())
        )
        self.client = self.app.test_client()

    def test_returns_processed_image_and_face_count(self):
        response = self.client.post(
            "/api/blur",
            data={"image": (BytesIO(b"image"), "image.jpg")},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/jpeg")
        self.assertEqual(response.headers["X-Faces-Found"], "2")

    def test_rejects_uploads_over_configured_limit(self):
        response = self.client.post(
            "/api/blur",
            data={"image": (BytesIO(b"x" * 2048), "image.jpg")},
        )

        self.assertEqual(response.status_code, 413)
        self.assertIn("error", response.get_json())

    def test_rejects_requests_when_rate_limited(self):
        self.rate_limiter.allowed = False
        response = self.client.post("/api/blur")

        self.assertEqual(response.status_code, 429)

    def test_routes_have_independent_dependencies(self):
        other_app = Flask("other")
        other_app.register_blueprint(
            create_routes(AllowAll(allowed=False), FakePhotoService())
        )

        first_response = self.client.post(
            "/api/blur",
            data={"image": (BytesIO(b"image"), "image.jpg")},
        )
        second_response = other_app.test_client().post(
            "/api/blur",
            data={"image": (BytesIO(b"image"), "image.jpg")},
        )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 429)


if __name__ == "__main__":
    unittest.main()
