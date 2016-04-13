from base import BaseWorker
from multiprocessing import Process


class ProcessWorker(Process, BaseWorker):
    def __init__(self, *args, **kwargs):
        Process.__init__(self)
        BaseWorker.__init__(self, *args, **kwargs)

    def start_work(self):
        self.start()

    def wait_work_finish(self):
        self.join()

    def run(self):
        self._internal_do_work()
