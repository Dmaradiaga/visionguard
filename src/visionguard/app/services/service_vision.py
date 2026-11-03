import numpy as np
import cv2


class PhotoService:
    def __init__(self):
        self.face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        if self.face_detector.empty():
            raise RuntimeError("No se pudo cargar el detector de rostros.")

    def blur_faces(self, image_file) -> tuple[np.ndarray, int]:
        """Lee una imagen, difumina los rostros detectados y la devuelve."""
        image_bytes = np.frombuffer(image_file.read(), dtype=np.uint8)
        image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("No se pudo leer la imagen")

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(
            gray_image,
            scaleFactor=1.1,
            minNeighbors=4,
        )

        for x, y, width, height in faces:
            face_region = image[y:y + height, x:x + width]
            image[y:y + height, x:x + width] = cv2.blur(face_region, (30, 30))

        return image, len(faces)