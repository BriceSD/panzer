""" constants for panzer code """
import os

REQUIRE_PANDOC_ATLEAST = "1.12.1"

DEFAULT_SUPPORT_DIR = os.path.join(os.path.expanduser('~'), '.panzer')

ENCODING = 'utf8'

# keys to access type and content of metadata fields
T = 't'
C = 'c'

# list of 'kind' of items on runlist, in order they should run
RUNLIST_KIND = ['preflight',
                'filter',
                'postprocess',
                'postflight',
                'cleanup']

# 'status' of items on runlist
QUEUED = 'queued'
RUNNING = 'running'
FAILED = 'failed'
DONE = 'done'

# ast of an empty pandoc document
EMPTY_DOCUMENT = [{'unMeta': {}}, []]
