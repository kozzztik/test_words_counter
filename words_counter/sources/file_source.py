from base import BaseSourceStream
import os


class FileSource(BaseSourceStream):
    def __enter__(self):
        # open source here if needed
        self.f = open(self.path, 'rb')
        self.f.seek(self.pos_start)
        return self

    def __exit__(self, ext, exv, trb):
        self.f.close()

    def _read_buffer(self, buffer_size):
        """
        Read buffer from source
        :return:
        """
        return self.f.read(buffer_size)

    @classmethod
    def source_size(cls, path):
        return os.path.getsize(path)
