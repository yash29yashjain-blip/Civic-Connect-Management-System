
from threading import Thread, Lock


def run_counter_demo(worker_count=4, increments_per_worker=1000):
    """Demonstrate a race-free shared counter using a mutex lock."""
    if worker_count <= 0 or increments_per_worker <= 0:
        raise ValueError("Worker and increment counts must be positive.")

    counter = 0
    lock = Lock()

    def worker():
        nonlocal counter
        for _ in range(increments_per_worker):
            with lock:
                counter += 1

    threads = [
        Thread(target=worker)
        for _ in range(worker_count)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return {
        "workers": worker_count,
        "increments_per_worker": increments_per_worker,
        "expected_counter": worker_count * increments_per_worker,
        "actual_counter": counter,
        "mutex_used": True
    }
