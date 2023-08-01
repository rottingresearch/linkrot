from queue import Queue
from linkrot import threadpool


def test_worker():
    tasks = Queue()
    worker = threadpool.Worker(tasks)
    assert worker.is_alive()
    tasks.put(lambda: print("Hello, world!"))
    tasks.put(lambda: print("Goodbye, world!"))
    tasks.join()
    assert not tasks.unfinished_tasks