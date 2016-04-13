import math

class CounterProcessor(object):
    def __init__(self, source_stream_class, worker_class, aggregator_class, splitter_class):
        self.source_stream_class = source_stream_class
        self.worker_class = worker_class
        self.aggregator_class = aggregator_class
        self.splitter_class = splitter_class

    def count_words(self, path, result_name, concurrency, read_buffer_size, settings, remove_mode=False):
        settings = settings.__dict__
        for k, v in settings.items():
            if (v.__class__.__name__ == 'module') or k.startswith('_'):
                del settings[k]
        source_length = self.source_stream_class.source_size(path)
        worker_length = int(math.ceil(source_length * 1.0 / concurrency))
        aggregator = self.aggregator_class(result_name, remove_mode=remove_mode, **settings.get('aggregator', {}))
        workers = [self.worker_class(i, worker_length, aggregator, self.source_stream_class, path, self.splitter_class,
                                     read_buffer_size, settings)
                   for i in range(concurrency)]
        for worker in workers:
            worker.start_work()

        for worker in workers:
            worker.wait_work_finish()
        return aggregator.finalize_results()
