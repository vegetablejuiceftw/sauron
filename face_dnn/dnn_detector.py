import os
from time import time

import cv2 as cv
import numpy as np


class DNNProcessor:

    def __init__(self) -> None:
        # Define paths
        base_dir = os.path.dirname(__file__)
        prototxt_path = os.path.join(base_dir, 'model_data/deploy.prototxt')
        caffemodel_path = os.path.join(base_dir, 'model_data/weights.caffemodel')

        # Read the model, each zoom needs a new instance
        self.zooms = [100, 200, 300]
        self.models = {
            zoom: cv.dnn.readNetFromCaffe(prototxt_path, caffemodel_path)
            for zoom in self.zooms
        }

    def process(self, frame, zoom=300):
        assert zoom in self.zooms
        model = self.models[zoom]

        h, w = frame.shape[:2]
        size = zoom
        blob = cv.dnn.blobFromImage(cv.resize(frame, (size, size)), 1.0, (size, size), (104.0, 177.0, 123.0))

        model.setInput(blob)
        detections = model.forward()

        position_results = []
        # Create frame around face
        for i in range(0, detections.shape[2]):
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            confidence = detections[0, 0, i, 2]

            # If confidence > 0.5, show box around face
            if confidence > 0.5:
                pos = (
                    startX,
                    startY,
                    endX - startX,
                    endY - startY,

                )
                position_results.append(pos)

        return position_results


if __name__ == '__main__':
    cap = cv.VideoCapture(0)

    processor = DNNProcessor()

    while cap.isOpened:
        ret, frame = cap.read()

        if frame is None:
            continue

        start = time()
        faces = processor.process(frame, 100)
        print(time() - start)
        for x, y, w, h in faces:
            cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            print(x, y, w, h)

        # cv.imshow('Capture - Face detection', frame)

        # if cv.waitKey(10) == 27:
        #     break
