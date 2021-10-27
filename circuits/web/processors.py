from .parsers import QueryStringParser


class _MultipartPart(object):
    def __init__(self, body):
        self._body = body
        self.file = body.fd
        self.headers = body.headers
        self.headerlist = list(self.headers.items())
        self.size = len(body)
        cd = body.headers.element('Content-Disposition')
        self.disposition = cd.value
        self.name = cd.params['name']
        self.filename = cd.filename
        self.content_type = body.mimetype.value
        self.charset = body.mimetype.charset

    def is_buffered(self):
        return True

    @property
    def value(self):
        return str(self._body)

    def save_as(self, path):
        with open(path, 'wb') as fp:
            pos = self.file.tell()
            try:
                self.file.seek(0)
                size = _copy_file(self.file, fp)
            finally:
                self.file.seek(pos)
        return size


def _copy_file(stream, target, maxread=-1, buffer_size=2 * 16):
    """Read from :stream and write to :target until :maxread or EOF."""
    size, read = 0, stream.read
    while 1:
        to_read = buffer_size if maxread < 0 else min(buffer_size, maxread - size)
        part = read(to_read)
        if not part:
            return size
        target.write(part)
        size += len(part)


def process_multipart(request, params):
    return _process_multipart(request.to_httoop(), params)


def _process_multipart(request, params):
    data = request.body.decode()
    for part in data or []:
        cd = part.headers.element('Content-Disposition')
        name = cd.params['name']
        if cd.filename:  # or not _MultipartPart(part).is_buffered():
            params[name] = _MultipartPart(part)
        else:
            params[name] = str(part)


def process_urlencoded(request, params, encoding='utf-8'):
    return _process_urlencoded(request.to_httoop(), params, encoding='utf-8')


def _process_urlencoded(request, params, encoding='utf-8'):
    p = {}
    p.update(dict(request.uri.query))
    p.update(dict(request.body.decode()))
    qs = QueryStringParser('')
    for i in p.items():
        qs.process(i)
    params.update(qs.result)


def process(request, params):
    request = request.to_httoop()
    request.body.headers = request.headers
    content_type = request.body.mimetype
    if not content_type:
        return

    if content_type.type == 'multipart':
        _process_multipart(request, params)
    if content_type.mimetype == 'application/x-www-form-urlencoded':
        _process_urlencoded(request, params, encoding=content_type.charset or 'utf-8')
