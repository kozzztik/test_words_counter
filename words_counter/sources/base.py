class BaseSourceStream(object):
    def __init__(self, path, pos_start, pos_end, buffer_size):
        """

        :param str path: Path to source, depends on realization
        :param int pos_start: start position in source for stream
        :param int pos_end: end position in source
        :param int buffer_size: read buffer size
        :return:
        """
        self.pos_start = pos_start or 0
        self.pos_end = pos_end
        self.current_pos = self.pos_start
        self.buffer_size = buffer_size
        self.path = path

    def __enter__(self):
        # open source here if needed
        return self

    def __exit__(self, ext, exv, trb):
        # close source here if needed
        pass

    def _read_buffer(self, buffer_size):
        """
        Read buffer from source
        :return:
        """
        raise NotImplementedError()

    @classmethod
    def source_size(cls, path):
        """
        Return total size of source
        :return: int
        """
        raise NotImplementedError

    def __iter__(self):
        return self

    def next(self):
        if not self.readable:
            raise StopIteration
        buffer_size = min(self.buffer_size, self.pos_end - self.current_pos)
        str_buffer = self._read_buffer(buffer_size)
        self.current_pos += self.buffer_size
        try:
            str_buffer = str_buffer.decode('windows-1251')
        except UnicodeError:
            pass
        return str_buffer

    @property
    def readable(self):
        return self.current_pos < self.pos_end


class StringSource(BaseSourceStream):
    def _read_buffer(self, buffer_size):
        return self.path[self.current_pos:self.current_pos + buffer_size]

    @classmethod
    def source_size(cls, path):
        return len(path)
