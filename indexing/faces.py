import cv2

def detect_faces(image):
    """
    Detect faces in an image.
    
    @param image: The input image in which to detect faces.
    """
    # Load the pre-trained face detection model with the specified input size
    height, width = image.shape[:2]
    detector = cv2.FaceDetectorYN.create("models/face_detection_yunet_2026may.onnx", "", (width, height))

    # Detect faces in the image
    _, faces = detector.detect(image)

    return [] if faces is None else faces