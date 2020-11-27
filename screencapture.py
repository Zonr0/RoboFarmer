# import cv2
import numpy as np
import win32ui
import win32con
import win32api


def get_windows_bytitle(title_text, exact = False):
    def _window_callback(hwnd, all_windows):
        all_windows.append((hwnd, win32gui.GetWindowText(hwnd)))
    windows = []
    win32ui.EnumWindows(_window_callback, windows)
    if exact:
        return [hwnd for hwnd, title in windows if title_text == title]
    else:
        return [hwnd for hwnd, title in windows if title_text in title]

def grab_window(title="Foo"):
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    hwin = get_windows_bytitle(title)
    # Get and dereference the handle to the window device context
    source_context = win32ui.CreateDCFromHandle(win32gui.GetWindowDC(hwin))
    image_buffer = source_context.CreateCompatibleDC()
    image = win32ui.CreateBitmap()
    image.CreateCombatibleBitmap(source_context, width, height)
    image_buffer.SelectObject(image)
    # Should probably look up what this does. I assume it copies it into the buffer.
    image_buffer.bitBlt((0, 0), (width, height), source_context, (left, top), win32con.SRCCOPY)

# def grab_screen(region=None):
#     hwin = win32gui.GetDesktopWindow()
#
#     if region:
#         left, top, x2, y2 = region
#         width = x2 - left + 1
#         height = y2 - top + 1
#     else:
#         width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
#         height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
#         left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
#         top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
#
#     hwindc = win32gui.GetWindowDC(hwin)
#     srcdc = win32ui.CreateDCFromHandle(hwindc)
#     memdc = srcdc.CreateCompatibleDC()
#     bmp = win32ui.CreateBitmap()
#     bmp.CreateCompatibleBitmap(srcdc, width, height)
#     memdc.SelectObject(bmp)
#     memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)
#
#     signedIntsArray = bmp.GetBitmapBits(True)
#     img = np.fromstring(signedIntsArray, dtype='uint8')
#     img.shape = (height, width, 4)
#
#     srcdc.DeleteDC()
#     memdc.DeleteDC()
#     win32gui.ReleaseDC(hwin, hwindc)
#     win32gui.DeleteObject(bmp.GetHandle())
#
#     return cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)