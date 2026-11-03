from flask import (
    Blueprint,
    current_app,
    request,
    jsonify,
    render_template,
    send_file
)

import cv2
import io
from werkzeug.exceptions import RequestEntityTooLarge

from visionguard.app.core.limiter import RateLimiter
from visionguard.app.services.service_vision import PhotoService

routes = Blueprint("routes", __name__)

rate_limiter: RateLimiter | None = None
photo_service: PhotoService | None = None


@routes.app_errorhandler(RequestEntityTooLarge)
def handle_large_upload(_error):
    return jsonify({
        "error": "La imagen supera el límite permitido."
    }), 413


def configure(
    rate_limiter_obj: RateLimiter,
    photo_service_obj: PhotoService,
) -> None:
    global rate_limiter
    global photo_service

    rate_limiter = rate_limiter_obj
    photo_service = photo_service_obj


@routes.route("/")
def home():
    return render_template("index.html")


@routes.route("/api/blur", methods=["POST"])
def blur():
    """
    Aplica blur a los rostros detectados y devuelve
    la imagen resultante.
    """

    if rate_limiter is None or photo_service is None:
        current_app.logger.error("Application services have not been configured")
        return jsonify({
            "error": "Servicio no disponible."
        }), 500

    client_ip = request.remote_addr or "unknown"

    if not rate_limiter.is_allowed(client_ip):
        return jsonify({
            "error": "Limite alcanzado"
        }), 429

    if "image" not in request.files:
        return jsonify({
            "error": "Es necesario una imagen."
        }), 400

    image_file = request.files["image"]

    try:
        processed_image, faces_found = (
            photo_service.blur_faces(image_file)
        )

        success, buffer = cv2.imencode(
            ".jpg",
            processed_image
        )

        if not success:
            return jsonify({
                "error": "No se pudo procesar la imagen."
            }), 500

        response = send_file(
            io.BytesIO(buffer.tobytes()),
            mimetype="image/jpeg",
            download_name="blurred.jpg"
        )

        response.headers["X-Faces-Found"] = str(faces_found)

        return response

    except ValueError as exc:
        return jsonify({
            "error": str(exc)
        }), 400

    except Exception:
        current_app.logger.exception("Failed to process uploaded image")
        return jsonify({
            "error": "Error interno."
        }), 500

