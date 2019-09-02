from time import time, sleep

import cv2 as cv
import SharedArray as sa
import numpy as np

cap = cv.VideoCapture(0)
# cap.set(cv.CAP_PROP_FPS, 29)
# cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
# cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)

ret, frame = cap.read()
frame: np.ndarray
shape = frame.shape
dtype = frame.dtype
print(shape)


def get_publisher(channel: str, shape: tuple, dtype) -> np.ndarray:
    # Create an array in shared memory.
    short_name = channel.split("://")[-1]
    mapping = {e.name.decode(): e for e in sa.list()}
    if short_name in mapping:
        array = mapping[short_name]
        if array.dtype == dtype and array.dims == shape:
            return sa.attach(channel)
        sa.delete(short_name)

    return sa.create(channel, shape, dtype)


frame = get_publisher("shm://test", shape, dtype)

start = time()
counter = 1
while cap.isOpened:
    counter += 1
    cap.read(frame)

    if counter % 30 == 0:
        print(1 / (time() - start))
    start = time()

    # cv.imshow('Capture - producer', frame)
    # if cv.waitKey(1) == 27:
    #     break
