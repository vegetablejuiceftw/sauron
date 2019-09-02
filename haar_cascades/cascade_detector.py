import os

import cv2 as cv


class Topics:
    face = 'haarcascade_frontalface_default.xml'
    eye = 'haarcascade_eye.xml'
    body = 'haarcascade_upperbody.xml'
    face_lbp = 'lbpcascade_frontalface.xml'


class CascadeProcessor:

    def __init__(self, topic) -> None:
        # Define paths
        base_dir = os.path.dirname(__file__)
        topic_path = os.path.join(base_dir, topic)
        self.cascade_detector = cv.CascadeClassifier(topic_path)

    def process(self, frame, zoom: float):
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame_gray = cv.resize(frame_gray, (0, 0), fx=zoom, fy=zoom)

        # optional
        frame_gray = cv.equalizeHist(frame_gray)

        min_size = int(32 * zoom)

        results = self.cascade_detector.detectMultiScale(frame_gray, minNeighbors=4, minSize=(min_size, min_size))

        position_results = []
        for x, y, w, h in results:
            position_results.append(
                (
                    int(x / zoom),
                    int(y / zoom) - 20,
                    int(w / zoom),
                    int(h / zoom) + 20,
                ),
            )

        return position_results
