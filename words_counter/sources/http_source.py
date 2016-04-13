from base import BaseSourceStream
import requests


class HTTPSource(BaseSourceStream):
    def _read_buffer(self, buffer_size):
        """
        Read buffer from source
        :return:
        """
        headers = {'Range': 'bytes=%s-%s' % (self.current_pos, self.current_pos + buffer_size - 1)}
        return requests.get(self.path, headers=headers, stream=True).raw.read(buffer_size)

    @classmethod
    def source_size(cls, path):
        return int(requests.head(path).headers['content-length'])
