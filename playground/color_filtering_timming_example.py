import cv2 as cv
import numpy as np


def nothing(x):
    pass


# Create a window
cv.namedWindow('image')

# create trackbars for color change
cv.createTrackbar('LH', 'image', 29, 255, nothing)
cv.createTrackbar('LS', 'image', 60, 255, nothing)
cv.createTrackbar('LV', 'image', 56, 255, nothing)

cv.createTrackbar('UH', 'image', 81, 255, nothing)
cv.createTrackbar('US', 'image', 144, 255, nothing)
cv.createTrackbar('UV', 'image', 173, 255, nothing)

camera = cv.VideoCapture(0)

while True:
    status, image = camera.read()

    # image = cv.GaussianBlur(image, (7, 7), 0)
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    lh = cv.getTrackbarPos('LH', 'image')
    ls = cv.getTrackbarPos('LS', 'image')
    lv = cv.getTrackbarPos('LV', 'image')
    uh = cv.getTrackbarPos('UH', 'image')
    us = cv.getTrackbarPos('US', 'image')
    uv = cv.getTrackbarPos('UV', 'image')

    lower_range = np.array([lh, ls, lv])
    upper_range = np.array([uh, us, uv])

    mask = cv.inRange(hsv, lower_range, upper_range)
    mask = cv.erode(mask, None, iterations=4)
    # kernel = np.ones((5, 5), np.uint8)

    # mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)

    res = cv.bitwise_and(image, image, mask=mask)

    contours, hierarchy = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    points = [cv.boundingRect(cnt) for cnt in contours]

    for x, y, w, h in points:
        cv.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

    cv.imshow('image', image)
    cv.imshow('mask', res)

    k = cv.waitKey(5) & 0xFF
    if k == 27:
        break

cv.destroyAllWindows()
