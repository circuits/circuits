from pwd import getpwnam
from grp import getgrnam
from traceback import format_exc
from os import getuid, setgroups, setgid, setuid, umask


from circuits.core import handler, BaseComponent


class DropPrivileges(BaseComponent):

    def init(self, user="nobody", group="nobody", **kwargs):
        self.user = user
        self.group = group

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

            # Ensure a very conservative umask
            umask(077)
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
