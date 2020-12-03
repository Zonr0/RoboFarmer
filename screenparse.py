import gamestate
import cv2
import numpy as np
import pytesseract

# Need to find out why this isn't autoloading from the path
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

class LocationConstants:
    # The timeblock contains the season, the date, the day, the time, and current gold.
    TIME_BLOCK_POS = (1600, 10)
    TIME_BLOCK_SIZE = (450, 250)

def find_time(image : np.array):
    # First, lets crop to an area of the screen we care about and save us some pixels.
    x,y = LocationConstants.TIME_BLOCK_POS
    w,h = LocationConstants.TIME_BLOCK_SIZE

    image = image[y:y + h, x:x + w]

    cv2.imshow('OCR-Preview', image)
    cv2.waitKey(0)

    # Whenever we can, work in grayscale. It vastly simplifies most computer vision problems.
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Get rid of pixels that aren't the right brightness. Set them to black.

    cv2.imshow('OCR-Preview', gray)
    cv2.waitKey(0)

    # Simple thresholding. We won't use this because the game could be paused, thus changing our lighting.
    ret, thresh = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY)
    # Example seen online
    # ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    # Adaptive thresholding based on the surrounding light
    #thresh = cv2.adaptiveThreshold(gray, 100, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, blockSize=11, C=2)
    # Otsu's Thresholding
    # ret,thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    # Define the area we are interested in with a rectangle:
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
    # Expand the detected area
    dilation = cv2.dilate(thresh, rect_kernel, iterations=1)
    cv2.imshow('OCR-Preview', dilation)
    cv2.waitKey(0)
    # Find the contours in the bounded area.
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    marked_image = gray.copy()
    found_text = list()
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Drawing a rectangle on copied image
        rect = cv2.rectangle(marked_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Cropping the text block for giving input to OCR
        cropped = marked_image[y:y + h, x:x + w]
        ret, thresh = cv2.threshold(cropped, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
        cv2.imshow('OCR-Preview', thresh)
        cv2.waitKey(0)

        # Apply OCR on the cropped image
        found_text.append(pytesseract.image_to_string(thresh))

    cv2.imshow('OCR-Preview',marked_image,)
    cv2.waitKey(0)
    cv2.destroyWindow('OCR-Preview')
    print(found_text)
    return(found_text[0])
