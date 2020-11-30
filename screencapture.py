import cv2
import numpy as np
from ctypes import *
import win32ui
import win32con
import win32api
import win32gui
import asyncio
# from asyncio.queues import *
import threading
import queue

def get_windows_list():
    def _window_callback(hwnd, all_windows):
        all_windows.append((hwnd, win32gui.GetWindowText(hwnd)))
    windows = []
    win32gui.EnumWindows(_window_callback, windows)
    return windows

def get_windows_bytitle(title_text, exact = False):
    def _window_callback(hwnd, all_windows):
        all_windows.append((hwnd, win32gui.GetWindowText(hwnd)))
    windows = []
    win32gui.EnumWindows(_window_callback, windows)
    if exact:
        return {title :  hwnd for hwnd, title in windows if title_text == title}
    else:
        return {title : hwnd for hwnd, title in windows if title_text in title}


def screenshot_routine(title : str, image_queue : queue.Queue, stop_event : threading.Event):
    while not stop_event.is_set():
        image = grab_window(title)
        try:
            image_queue.put_nowait(image)
        except queue.Full:
            continue  # Just drop the frame and try again after
    return


def image_preview_routine(image_queue : queue.Queue, stop_event : threading.Event, consume=True):
    try:
        while not stop_event.is_set():
            img = image_queue.get()
            if consume:
                image_queue.task_done()
            cv2.imshow("Preview", img)
            cv2.waitKey(1)
    finally:
        cv2.destroyAllWindows()
    return


def grab_window(title="Foo"):
    # width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    # height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    # left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    # top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    hwin = win32gui.FindWindow(None, title)  # get_windows_bytitle(title)[0]
    left, top, right, bot = win32gui.GetWindowRect(hwin)
    width = right - left
    height = bot - top

    # Get and dereference the handle to the window device context
    hwindc = win32gui.GetWindowDC(hwin)
    source_context = win32ui.CreateDCFromHandle(hwindc)
    writer_context = source_context.CreateCompatibleDC()

    bmp_object = win32ui.CreateBitmap()
    bmp_object.CreateCompatibleBitmap(source_context, width, height)

    writer_context.SelectObject(bmp_object)
    # Copy from one device context into another
    # Destination coordinates seem to be relative to the context and not absolute screen coordinates. Therefore we pass
    # 0,0 instead of top and left.
    writer_context.BitBlt((0, 0), (width, height), source_context, (0, 0), win32con.SRCCOPY)

    image_array = np.frombuffer(bmp_object.GetBitmapBits(True), dtype='uint8')  # These are signed
    image_array.shape = (height, width, 4)

    source_context.DeleteDC()
    writer_context.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    win32gui.DeleteObject(bmp_object.GetHandle())

    return cv2.cvtColor(image_array, cv2.COLOR_BGRA2RGB)

def test_screencapture():
    IMAGE_BUFFER_SIZE = 12
    found = get_windows_bytitle("Notepad")
    window_title = tuple(found.keys())[0]

    # Threading setup
    image_queue = queue.Queue(IMAGE_BUFFER_SIZE)
    capture_stop_event = threading.Event()

    screenshot_thread = threading.Thread(target=screenshot_routine, args=(window_title,image_queue,capture_stop_event), daemon=True)
    preview_thread = threading.Thread(target=image_preview_routine, args=(image_queue,capture_stop_event), daemon=True)
    threads = [screenshot_thread, preview_thread] # For easy reference later. In the order that they must be stopped.
    for t in threads:
        t.start()
    print("Tasks started. Type 'quit' to exit")

    cmd = ""
    while cmd.lower() != 'q':
        cmd = input("Type 'quit' to exit: ")[0]

    # Send kill signal to both threads and then wait for each to stop
    print("Quitting")
    capture_stop_event.set()
    screenshot_thread.join(timeout=10) # Need to stop this one first
    preview_thread.join(timeout=10)
    print("Threads finished. Exiting.")
    return

if __name__ == '__main__':
    test_screencapture()

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