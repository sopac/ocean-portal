#!/usr/bin/env python

RSYNC_COMMAND = "rsync -n -ruvx --delete-excluded --include='*/' %(args)s --exclude='*' %(source)s %(dest)s"

# file globs to transfer
INCLUDE_LIST = [ '*.nc',
                 '*.nc4',
                 '*.txt',
               ]
# file globs to exclude from above
EXCLUDE_LIST = [ '*_preliminary.nc',
                 'new/*',
                 'archive/*',
               ]

import sys
import os.path
import subprocess

from ocean import util
from ocean.util import serverConfig

to_server = sys.argv[1]

from_data = util.get_server_config()['dataDir']
to_data = serverConfig.servers[to_server]['dataDir']

for (dataset, from_datadir), to_datadir in zip(from_data.items(), to_data.values()):
    try:
        config = __import__('ocean.%s.%sConfig' % (dataset, dataset),
                fromlist=[''])
    except ImportError:
        print >> sys.stderr, "Could not import %sConfig, skipping" % (dataset)
        continue

    class_name = '%sConfig' % (dataset.title())

    if not hasattr(config, class_name):
        print >> sys.stderr, "No %s class, skipping" % (class_name)
        continue

    config_class = getattr(config, class_name)()

    if not hasattr(config_class, 'subDirs'):
        print >> sys.stderr, "%s.subDirs not defined" % (class_name)
        continue

    subdirs = config_class.subDirs

    for subdir in subdirs:
        from_dir = '%s/' % (os.path.join(from_datadir, subdir))
        to_dir = '%s:%s/' % (to_server, os.path.join(to_datadir, subdir))

        args = []
        args += map(lambda i: "--exclude='%s'" % i, EXCLUDE_LIST)
        args += map(lambda i: "--include='%s'" % i, INCLUDE_LIST)

        command = RSYNC_COMMAND % { 'source': from_dir,
                                    'dest': to_dir,
                                    'args': ' '.join(args),
                                  }
        print command
        subprocess.call(command, shell=True)
