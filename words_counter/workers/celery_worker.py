from base import BaseWorker
from celery import Celery
import settings


class CeleryWorker(BaseWorker):
    _task = None

    def start_work(self):
        self._task = words_counter.apply_async(kwargs={'worker': self})

    def wait_work_finish(self):
        assert self._task is not None
        self._task.get()

    def do_work(self):
        self._internal_do_work()


celery = Celery()
celery.config_from_object(settings.CELERY_SETTINGS)

@celery.task()
def words_counter(worker):
    """
    Celery task for counting
    :param CeleryWorker worker: worker
    :return:
    """
    worker.do_work()


