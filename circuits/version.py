# Package:  version
# Date:     18th October 2013
# Author:   James Mills, j dot mills at griffith dot edu dot au

"""Version Module

So we only have to maintain version information in one place!
"""

version_info = (3, 0, 0, "dev", 1)  # (major, minor, patch, dev, build)
version = "{0:s}.{1:s}{2:d}".format(".".join(map(str, version_info[:3])), version_info[-2], version_info[-1])
