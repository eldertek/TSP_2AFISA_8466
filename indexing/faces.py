import cv2
import numpy as np

from indexing.models import Face, Person

SIMILARITY_THRESHOLD = 0.363
MAX_IMAGE_DIMENSION = 1600


def resize_image_if_needed(image):
    """
    Resize the image if its dimensions exceed the maximum allowed size.

    @param image: The input image to be resized.
    """
    height, width = image.shape[:2]
    interpolation = (
        cv2.INTER_AREA if max(height, width) > MAX_IMAGE_DIMENSION else cv2.INTER_LINEAR
    )

    if max(height, width) > MAX_IMAGE_DIMENSION:
        scaling_factor = MAX_IMAGE_DIMENSION / max(height, width)
        new_width = int(width * scaling_factor)
        new_height = int(height * scaling_factor)
        resized_image = cv2.resize(
            image, (new_width, new_height), interpolation=interpolation
        )
        return (resized_image, scaling_factor)

    return (image, 1.0)


def detect_faces(image):
    """
    Detect faces in an image.

    @param image: The input image in which to detect faces.
    """
    resized_image, scale = resize_image_if_needed(image)

    # Load the pre-trained face detection model with the specified input size
    height, width = resized_image.shape[:2]
    detector = cv2.FaceDetectorYN.create(
        "models/face_detection_yunet_2026may.onnx", "", (width, height)
    )

    # Detect faces in the image
    _, faces = detector.detect(resized_image)

    if faces is None:
        return []

    if scale != 1.0:
        faces[:, :14] /= scale

    return faces


def extract_embedding(image, face):
    """
    Extract the embedding of a detected face.

    @param image: The input image containing the face.
    @param face: The bounding box of the detected face.
    """
    # Load the pre-trained face recognition model
    recognizer = cv2.FaceRecognizerSF.create(
        "models/face_recognition_sface_2021dec.onnx", ""
    )

    # Align the detected face
    aligned_face = recognizer.alignCrop(image, face)

    # Compute the embedding for the extracted face region
    embedding = recognizer.feature(aligned_face)

    return embedding.tobytes()


def assign_person(embedding_bytes):
    """
    Assign a person to a face based on the provided embedding.

    @param embedding_bytes: The embedding of the detected face in bytes.
    """

    vector = np.frombuffer(embedding_bytes, dtype=np.float32).reshape(1, -1)

    recognizer = cv2.FaceRecognizerSF.create(
        "models/face_recognition_sface_2021dec.onnx", ""
    )

    existing_faces = Face.objects.filter(person__isnull=False).select_related("person")

    best_person = None
    best_score = 0.0

    for face in existing_faces:
        db_vector = np.frombuffer(face.embedding, dtype=np.float32).reshape(1, -1)
        score = recognizer.match(vector, db_vector, cv2.FaceRecognizerSF_FR_COSINE)

        if score >= SIMILARITY_THRESHOLD:
            if score > best_score:
                best_score = score
                best_person = face.person

    return best_person if best_person else Person.objects.create(name="")
