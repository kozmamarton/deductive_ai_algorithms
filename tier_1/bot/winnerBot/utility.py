import multiprocessing
import time

def run_with_timeout(func, timeout=0.5):
    queue = multiprocessing.Queue()
    proc = multiprocessing.Process(target=func, args=[queue])
    proc.start()
    proc.join(timeout)

    if proc.is_alive():
        proc.terminate()
        proc.join()

    # Retrieve result if available
    if not queue.empty():
        return queue.get()
    else:
        return None