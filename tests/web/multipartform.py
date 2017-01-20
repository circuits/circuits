import itertools
from email.generator import _make_boundary
from mimetypes import guess_type


class MultiPartForm(dict):

    def __init__(self):
        self.files = []
        self.boundary = _make_boundary()

    def get_content_type(self):
        return "multipart/form-data; boundary=%s" % self.boundary

    def add_file(self, fieldname, filename, fd, mimetype=None):
        body = fd.read()
        if mimetype is None:
            mimetype = guess_type(filename)[0] or "application/octet-stream"
        self.files.append((fieldname, filename, mimetype, body))

    def bytes(self):
        parts = []
        part_boundary = bytearray("--%s" % self.boundary, "ascii")

        # Add the form fields
        parts.extend([
            part_boundary,
            bytearray(
                "Content-Disposition: form-data; name=\"%s\"" % k,
                "ascii"
            ),
            bytes(),
            v if isinstance(v, bytes) else bytearray(v, "ascii")
        ] for k, v in list(self.items()))

        # Add the files to upload
        parts.extend([
            part_boundary,
            bytearray(
                "Content-Disposition: form-data; name=\"%s\"; filename=\"%s\"" % (
                    fieldname, filename),
                "ascii"
            ),
            bytearray("Content-Type: %s" % content_type, "ascii"),
            bytearray(),
            body if isinstance(body, bytes) else bytearray(body, "ascii"),
        ] for fieldname, filename, content_type, body in self.files)

        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append(bytearray("--%s--" % self.boundary, "ascii"))
        res = bytearray()
        for item in flattened:
            res += item
            res += bytearray("\r\n", "ascii")
        return res
