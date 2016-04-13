class BaseSplitter(object):
    def __init__(self, source):
        self.source = source
        self.buffer_empty = False
        self.started_with_word = None
        self.finished_with_word = None

    def _split_buffer(self, str_buffer):
        """
        Split buffer to words.
        :param str str_buffer: str buffer to split
        :return: Generator
        """
        raise NotImplementedError

    def _starts_with_word(self, str_buffer):
        raise NotImplementedError

    def _finished_with_word(self, str_buffer):
        raise NotImplementedError

    def split(self):
        """
        Returns generator of words in source
        :return:
        """
        finished_with_word = False
        with self.source as source:
            last_buffer_word = None
            for str_buffer in source:
                last_word = None
                started_with_word = self._starts_with_word(str_buffer)
                if self.started_with_word is None:
                    self.started_with_word = started_with_word
                if (not started_with_word) and last_buffer_word:
                    yield last_buffer_word
                    last_buffer_word = None
                for word in self._split_buffer(str_buffer):
                    if last_word is not None:
                        yield last_word
                    if last_buffer_word is not None:
                        last_word = last_buffer_word + word
                        last_buffer_word = None
                    else:
                        last_word = word
                finished_with_word = self._finished_with_word(str_buffer)
                if finished_with_word:
                    last_buffer_word = last_word
                else:
                    yield last_word
            self.finished_with_word = finished_with_word
            if last_buffer_word is not None:
                yield last_buffer_word
