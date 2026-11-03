import numpy as np
import cv2

class PhotoService:
	def __init__(self):
		#Cargamos el detector al iniciar la app
		self.face_detector = cv2.CascadeClassifier(
			cv2.data.haarcascades +
            "haarcascade_frontalface_default.xml"
            )

	def blur_faces(self,image_file) -> tuple[np.ndarray,int]:
		"""
			Lee un imagen, aplica una difuminacion a los rostros
			y retorna las imagenes procesadas
		"""

		image_bytes = np.frombuffer(image_file.read(),dtype=np.uint8)

		image = cv2.imdecode(image_bytes,cv2.IMREAD_COLOR)

		if image is None:
			raise ValueError("No se pudo leer la imagen")

		gray_image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

		faces = self.face_detector(gray_image,scaleFactor=1.1,minNeighbors=4)

		for (x,y, width, height) in faces:
			face_region = image[y:y + height, x:x + width]
			image[y:y + height, x:x + width] = cv2.blur(face_region,(30,30))

		return image, len(faces)