
import itertools
import mimetools
from mimetypes import guess_type

class MultiPartForm(dict):

    def __init__(self):
        self.files = []
        self.boundary = mimetools.choose_boundary()

    def get_content_type(self):
        return "multipart/form-data; boundary=%s" % self.boundary

    def add_file(self, fieldname, filename, fd, mimetype=None):
        body = fd.read()
        if mimetype is None:
            mimetype = guess_type(filename)[0] or "application/octet-stream"
        self.files.append((fieldname, filename, mimetype, body))

    def __str__(self):
        parts = []
        part_boundary = "--%s" % self.boundary

        # Add the form fields
        parts.extend([
            part_boundary,
            "Content-Disposition: form-data; name=\"%s\"" % k,
            "",
            v
        ] for k, v in self.items())

        # Add the files to upload
        parts.extend([
            part_boundary,
            "Content-Disposition: file; name=\"%s\"; filename=\"%s\"" % (
                fieldname, filename),
            "Content-Type: %s" % content_type,
            "",
            body,
        ] for fieldname, filename, content_type, body in self.files)

        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append("--%s--" % self.boundary)
        flattened.append("")
        return "\r\n".join(flattened)
