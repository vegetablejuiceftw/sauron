from time import time, sleep

import cv2 as cv
import SharedArray as sa
import numpy as np

frame: np.ndarray = sa.attach("shm://test")

old = frame.copy()
start = time()

counter = 1
while True:
    s = time()
    counter += 1
    if counter % 60 == 0:
        frame: np.ndarray = sa.attach("shm://test")
        print("Fo %.6f" % (time() - s))

    if not np.array_equal(old, frame):
        old = frame.copy()

        estimated_cap_delay = time() - start
        if counter % 30 == 0:
            print(1 / estimated_cap_delay)
        start = time()
        sleep(estimated_cap_delay * 0.9)
    else:
        sleep(0.001)

        # continue
    # print(np.array_equal(old, frame))
    # cv.imshow('Client', frame)
    # if cv.waitKey(1) == 27:
    #     break
