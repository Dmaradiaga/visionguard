import unittest
from io import BytesIO
from unittest.mock import Mock

import cv2
import numpy as np

from visionguard.app.services.service_vision import PhotoService


class PhotoServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = PhotoService()

    def test_blurs_detected_faces(self):
        detector = Mock()
        detector.detectMultiScale.return_value = np.array([[10, 10, 40, 40]])
        self.service.face_detector = detector

        image = np.full((80, 80, 3), 255, dtype=np.uint8)
        success, encoded = cv2.imencode(".jpg", image)
        self.assertTrue(success)

        processed, count = self.service.blur_faces(BytesIO(encoded.tobytes()))

        self.assertEqual(processed.shape, image.shape)
        self.assertEqual(count, 1)
        detector.detectMultiScale.assert_called_once()

    def test_rejects_invalid_image_data(self):
        with self.assertRaisesRegex(ValueError, "No se pudo leer"):
            self.service.blur_faces(BytesIO(b"not an image"))


if __name__ == "__main__":
    unittest.main()
