from contextlib import contextmanager, closing
from cStringIO import StringIO
import requests


class iterator_to_file(object):
    """Incomplete implementation of a file-like object on top of
    an iterator.
    """
    def __init__(self, it):
        self._it = it
        self._buf = ''

    def __iter__(self):
        return self

    def close(self):
        pass

    def read(self, size=-1):
        if size >= 0:
            return self._read_n(size)
        else:
            with closing(StringIO()) as res:
                buf = self._read_n(4096)
                res.write(buf)
                while len(buf) == 4096:
                    buf = self._read_n(4096)
                    res.write(buf)
                return res.getvalue()

    def _read_n(self, size):
        while len(self._buf) < size:
            try:
                data = next(self._it)
            except StopIteration:
                if len(self._buf) == 0:
                    raise
                else:
                    res = self._buf
                    self._buf = ''
                    return res
            self._buf += data
            if len(data) == 0:
                break
        if len(self._buf) > size:
            res = self._buf[:size]
            self._buf = self._buf[size:]
        else:
            len(self._buf)
            res = self._buf
            self._buf = ''
        return res

    def next(self):
        return self._it()


class stream_from_request(object):
    """Build streamed file-like instances from an HTTP request.
    """
    def __init__(self, url, method='GET', **kwargs):
        """
        :param basestring url:
          Resource URL

        :param basestring method:
          HTTP method

        :param dict kwargs:
          Optional parameters given to the `requests.sessions.Session.request`
          member method.
        """
        self.__url = url
        self.__method = method
        self.__kwargs = kwargs.copy()

    @contextmanager
    def open(self, session=None):
        """
        :param requests.Session session:
          Optional requests session


        :return:
          file-like object over the decoded bytes
        """
        self.__kwargs.update(stream=True)
        session = session or requests
        resp = session.request(self.__method, self.__url, **self.__kwargs)
        try:
            yield iterator_to_file(iter(resp))
        finally:
            resp.close()
