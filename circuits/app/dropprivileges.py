from grp import getgrnam
from os import getuid, setgid, setgroups, setuid, umask
from pwd import getpwnam
from traceback import format_exc

from circuits.core import BaseComponent, handler


class DropPrivileges(BaseComponent):

    def init(self, user="nobody", group="nobody", umask=0o077, **kwargs):
        self.user = user
        self.group = group
        self.umask = umask

    def drop_privileges(self):
        if getuid() > 0:
            # Running as non-root. Ignore.
            return

        try:
            # Get the uid/gid from the name
            uid = getpwnam(self.user).pw_uid
            gid = getgrnam(self.group).gr_gid
        except KeyError as error:
            print("ERROR: Could not drop privileges {0:s}".format(error))
            print(format_exc())
            raise SystemExit(-1)

        try:
            # Remove group privileges
            setgroups([])

            # Try setting the new uid/gid
            setgid(gid)
            setuid(uid)

            if self.umask is not None:
                umask(self.umask)
        except Exception as error:
            print("ERROR: Could not drop privileges {0:s}".format(error))
            print(format_exc())
            raise SystemExit(-1)

    @handler("ready", channel="*")
    def on_ready(self, server, bind):
        try:
            self.drop_privileges()
        finally:
            self.unregister()
