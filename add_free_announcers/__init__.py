__version__ = '1.0.0'

from argparse import ArgumentParser
from enum import unique
from os.path import exists, join, split
from os import makedirs
from glob import iglob
from pprint import pprint
from typing import Container, Iterable, Set

from .config import TORRENT_DIR, TRACKERS_LIST_URL, OUTPUT_TORRENT_DIR
from .getlist import fetch_sources
from .encode import bencode, bdecode, DecodingException


parser = ArgumentParser()

parser.add_argument('--version', action='version', version=f'add-free-announcers {__version__}')
parser.add_argument(
    '--torrent-dir', '-td',
    help='Folder taht contains torrents to process,'
    ' when omitted defaults to TORRENT_DIR env variable',
    default=TORRENT_DIR
)
parser.add_argument(
    '--trackers',
    nargs='+',
    help='List of URI to tracker lists, when ommited'
    ' TRACKERS_LIST_URL env variable is used, if there is no varibale'
    ' fallback value is https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all.txt',
    default=[TRACKERS_LIST_URL]
)
parser.add_argument(
    '--tracker-list','-tl',
    action="append",
    help="Add a single tracker list to already present ones"
)
parser.add_argument(
    '--output', '-o',
    help='Path to a folder to put processed torrents into',
    default=OUTPUT_TORRENT_DIR
)


def iter_torrents(directory: str):
    return iglob(join(directory, '*.torrent'))


def process_file(filepath: str, output_dir: str, announcers: Iterable[str]):
    filename = split(filepath)[1]
    
    print(f'{filename!r}', end=' ')
    
    with open(filepath, 'rb') as file:
        raw_bytes = file.read()

    try:
        data = bdecode(raw_bytes)
    except DecodingException:
        print('FAILED! Decoding error!')
        return
    if not isinstance(data, dict):
        print('FAILED! Invalid data structure!')
        return
    
    # POV: you decide it's not cool enough to spend 
    # 5 lines of code to add trackers to announce-list
    data.setdefault('announce-list', []).extend(([i] for i in announcers))
    
    pack_back = bencode(data)
    with open(join(output_dir, filename), 'wb') as file:
        file.write(pack_back)
    
    print('OK')


def main():
    args = parser.parse_args()
    
    td = args.torrent_dir
    print(f'Processing torrents in {td!r}')
    if not exists(td):
        parser.error(f'TORRENT_DIR {td!r} does not exist!')

    output = args.output or OUTPUT_TORRENT_DIR or join(td, 'announcers_added')
    
    print(f'Output dir is {output!r}')
    if not exists(output):
        makedirs(output)
    
    trackers_lists_set = set(args.trackers + (args.tracker_list or []))
    
    print('----\nUsing tracker lists at:\n' + 
          '\n'.join(trackers_lists_set))
    
    trackers = fetch_sources(trackers_lists_set)
    
    print('\n----\nProcessing files:')
    
    for i in iter_torrents(td):
        process_file(i, output, trackers)
