import screenparse
import screencapture as scap
import threading
import queue
import gamestate
import copy
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import time
from collections import deque

IMAGE_BUFFER_SIZE = 12


class ThreadManager:
    """Singleton struct tracking threads and cross-thread state."""
    MAX_WORKERS = 3
    img_capture_queue: queue.Queue = None
    img_preview_queue: queue.Queue = None
    threads = list() # Used for core looping threads
    capture_stop_event = threading.Event()
    preview_stop_event = threading.Event()
    executor = ThreadPoolExecutor(MAX_WORKERS) # Used for independent tasks with well defined end states
    img_parse_performance = deque(maxlen=300)

    @staticmethod
    def get_performance():
        tick_times = np.array(ThreadManager.img_parse_performance)
        print(f"Mean: {tick_times.mean()}, Max: {tick_times.max()}, Min: {tick_times.min()}, Ticks/s {1 / tick_times.mean()}")



def get_and_exec_cmd():
    valid_commands = ['q', 'time']
    cmd = ""
    while cmd.lower() != 'q':
        cmd = input("Enter command (q to exit) ")
        if 'time' in cmd:
            screenparse.find_time(ThreadManager.img_capture_queue.get())
        if 'perf' in cmd:
            ThreadManager.get_performance()


def image_parsing_loop(game: gamestate.Game, mng: ThreadManager):
    tick_times = (0,0,0,0,0,0,0,0,0,0)
    current_tick = 1 # Start at 1 so we don't try to hit every tick threshold at once at startup.
    # This state is read only, only updated at the end of the tick. No need to worry about thread safety. If we just
    # need to read something, we don't want to block other tasks, and we should work off our understanding of our last
    # known stable state.
    read_only_state = game
    parse_futures = list()
    ex = mng.executor
    while not mng.capture_stop_event.is_set():
        tick_start_time = time.perf_counter()
        # This state contains the pending changes to the state. It ensures only one write at a time
        # to avoid race conditions
        write_state = copy.deepcopy(read_only_state)
        frame = mng.img_capture_queue.get()
        # Potentially, we could rewrite this to be fancy for shorter code and dynamic modification of what gets executed
        # on what tick.
        ## EVERY FRAME ##
        try:
            mng.img_preview_queue.put_nowait(frame)
        except queue.Full:
            pass  # Just drop the frame and try again next tick
        # Null task, to make sure we have some kind of task every frame.
        parse_futures.append(ex.submit(lambda : 0))

        ## EVERY 05 TICKS ##
        if current_tick % 5 == 0:
            pass

        ## EVERY 10 TICKS ##
        if current_tick % 10 == 0:
            pass
            #parse_futures.append(ex.submit(screenparse.find_time))

        ## EVERY 30 TICKS ##
        if current_tick % 30 == 0:
            pass

        ## EVERY 60 TICKS ##
        if current_tick % 60 == 0:
            pass

        ## EVERY 100 TICKS ##
        if current_tick % 100 == 0:
            pass

        ## EVERY 300 TICKS ##
        if current_tick % 300 == 0:
            pass

        ## EVERY 600 TICKS ##
        if current_tick % 600 == 0:
            current_tick = 0

        for task in parse_futures:
            task.result(timeout=10)  # Block until all results are finished.

        # Update our state. Shallow copy so we update our primary state. Note that we can't just reassign the reference,
        # or we will lose the updated values outside of this thread.
        read_only_state = copy.copy(write_state)
        current_tick += 1
        mng.img_capture_queue.task_done()

        tick_end_time = time.perf_counter()
        mng.img_parse_performance.appendleft(tick_end_time - tick_start_time)




def main():
    found = scap.get_windows_bytitle("STORY OF SEASONS")
    window_title = tuple(found.keys())[0]

    # Threading setup
    ThreadManager.img_capture_queue = queue.Queue(IMAGE_BUFFER_SIZE)  # Queue for images as they are scapped
    ThreadManager.img_preview_queue = queue.Queue(IMAGE_BUFFER_SIZE)  # Queue for images in the real-time preview

    screenshot_thread = threading.Thread(target=scap.screenshot_routine,
                                         args=(
                                             window_title, ThreadManager.img_capture_queue, ThreadManager.capture_stop_event),
                                         daemon=True)
    image_parse_thread = threading.Thread(target=image_parsing_loop,
                                          args=(gamestate.Game, ThreadManager), daemon=True)
    preview_thread = threading.Thread(target=scap.image_preview_routine,
                                      args=(ThreadManager.img_capture_queue, ThreadManager.capture_stop_event), daemon=True)
    ThreadManager.threads = [screenshot_thread,
                             image_parse_thread,
                             preview_thread,
                             ]  # For easy reference later. In the order that they must be stopped.
    for t in ThreadManager.threads:
        t.start()
    print("Tasks started. Type 'quit' to exit")

    get_and_exec_cmd()
    # screenparse.find_time(ThreadManager.img_capture_queue.get())

    # Send kill signal to both threads and then wait for each to stop
    print("Quitting")
    ThreadManager.capture_stop_event.set()
    ThreadManager.preview_stop_event.set()
    screenshot_thread.join(timeout=10)  # Need to stop this one first
    preview_thread.join(timeout=10)
    print("Threads finished. Exiting.")
    return


if __name__ == '__main__':
    main()
