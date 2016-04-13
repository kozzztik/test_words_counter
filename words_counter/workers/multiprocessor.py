from base import BaseWorker
from multiprocessing import Process, Event


class ProcessWorker(Process, BaseWorker):
    def __init__(self, *args, **kwargs):
        Process.__init__(self)
        BaseWorker.__init__(self, *args, **kwargs)
        self.finish_event = Event()

    def start_work(self):
        self.start()

    def wait_work_finish(self):
        self.finish_event.wait()

    def run(self):
        self._internal_do_work()
        self.finish_event.set()
