class BaseWorker(object):
    def __init__(self, num, worker_length, aggregator, source_stream_class, path, splitter_class, read_buffer_size,
                 settings):
        self.num = num
        self.source_steam = source_stream_class(path, num * worker_length, (num + 1) * worker_length, read_buffer_size)
        self.splitter = splitter_class(self.source_steam)
        self.aggregator = aggregator.attach_to_worker(self.num)
        self.settings = settings

    def start_work(self):
        raise NotImplementedError

    def wait_work_finish(self):
        raise NotImplementedError

    def _internal_do_work(self):
        last_word = None
        first_word = None
        with self.aggregator as aggregator:
            for word in self.splitter.split():
                if first_word is None:
                    if self.splitter.started_with_word:
                        first_word = word
                        continue
                    else:
                        first_word = ''
                if last_word is not None:
                    aggregator.aggregate(last_word)
                last_word = word
            if last_word and (not self.splitter.finished_with_word):
                aggregator.aggregate(last_word)
                last_word = ''
            aggregator.border_words(self.num, first_word, last_word)


class SimpleWorker(BaseWorker):
    def start_work(self):
        self._internal_do_work()

    def wait_work_finish(self):
        pass
