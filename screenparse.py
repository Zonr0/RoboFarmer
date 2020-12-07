import gamestate
import cv2
import numpy as np
import pytesseract
import gamestate

# Need to find out why this isn't autoloading from the path
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


class LocationConstants:
    # The timeblock contains the season, the date, the day, the time, and current gold.
    TIME_BLOCK_POS = (1600, 30)
    TIME_BLOCK_SIZE = (275, 210)
    QUICK_SEASON_POS = (TIME_BLOCK_POS[0] + 15, TIME_BLOCK_POS[1])
    QUICK_SEASON_SIZE = (150, 45)
    QUICK_DAY_POS = (TIME_BLOCK_POS[0] + 5, TIME_BLOCK_POS[1] + 40)
    QUICK_DAY_SIZE = (160,45)
    QUICK_TIME_POS = (TIME_BLOCK_POS[0], TIME_BLOCK_POS[1] + 91)
    QUICK_TIME_SIZE = (170, 40)
    QUICK_MONEY_POS = (TIME_BLOCK_POS[0]+10, TIME_BLOCK_POS[1] + 175)
    QUICK_MONEY_SIZE = (260, 40)


def find_time_and_money(image: np.array, game: gamestate.Game):
    # First, lets crop to an area of the screen we care about and save us some pixels.
    x, y = LocationConstants.TIME_BLOCK_POS
    w, h = LocationConstants.TIME_BLOCK_SIZE

    image = image[y:y + h, x:x + w]

    # Whenever we can, work in grayscale. It vastly simplifies most computer vision problems.
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # cv2.imshow('OCR-Preview', gray)
    # cv2.waitKey(0)

    location_dict = {
        "season": {"pos": LocationConstants.QUICK_SEASON_POS,
                   "size": LocationConstants.QUICK_SEASON_SIZE, },
        "day": {"pos": LocationConstants.QUICK_DAY_POS,
                "size": LocationConstants.QUICK_DAY_SIZE, },
        "time": {"pos": LocationConstants.QUICK_TIME_POS,
                 "size": LocationConstants.QUICK_TIME_SIZE, },
        "money": {"pos": LocationConstants.QUICK_MONEY_POS,
                  "size": LocationConstants.QUICK_MONEY_SIZE, },

    }
    found_text = list()
    for coords in location_dict.values():
        # print(coords)
        x, y = map(lambda i, j : i - j, coords['pos'], LocationConstants.TIME_BLOCK_POS)
        w, h = coords['size']

        image = gray[y:y + h, x:x + w]

        ret, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
        found_text.append(pytesseract.image_to_string(thresh))
    #   print(found_text)
    #     cv2.imshow('OCR-Preview', thresh)
    #     cv2.waitKey(0)
    #
    # cv2.destroyWindow('OCR-Preview')
    # Clean up the text results.
    results = list()
    for item in found_text:
        tokenized = item.split('\n')
        results.append(tokenized[0])
    print(results)
    game.time.set_time_from_string(results[2])
    return


