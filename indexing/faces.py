import cv2


def detect_faces(image):
    """
    Detect faces in an image.

    @param image: The input image in which to detect faces.
    """
    # Load the pre-trained face detection model with the specified input size
    height, width = image.shape[:2]
    detector = cv2.FaceDetectorYN.create(
        "models/face_detection_yunet_2026may.onnx", "", (width, height)
    )

    # Detect faces in the image
    _, faces = detector.detect(image)

    return [] if faces is None else faces


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
