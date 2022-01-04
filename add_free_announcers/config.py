from os import getenv
from os.path import join
import sys


TRACKERS_LIST_URL = getenv('TRACKERS_LIST_URL', 'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all.txt')

if sys.platform == 'win32':
    TORRENT_DIR = 'C:\\temp'
else:
    TORRENT_DIR = '/tmp'

TORRENT_DIR = getenv('TORRENT_DIR', TORRENT_DIR)
OUTPUT_TORRENT_DIR = getenv('OUTPUT_TORRENT_DIR')