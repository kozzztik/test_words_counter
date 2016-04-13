from base import BaseWorker
import threading


class ThreadWorker(threading.Thread, BaseWorker):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)
        BaseWorker.__init__(self, *args, **kwargs)

    def start_work(self):
        self.start()

    def wait_work_finish(self):
        self.join()

    def run(self):
        self._internal_do_work()
