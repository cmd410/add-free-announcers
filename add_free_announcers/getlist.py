import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import cache
from typing import Iterable, Set
from urllib.request import urlopen

pool = ThreadPoolExecutor()

http_re = re.compile(r"https?://.+")


class SourceFailure(RuntimeError):
    """Failed to get resource under given URI
    """


@cache
def _fetch_list(uri: str) -> str:
    """Return list text from fiven URI
    
    On failure raises SourceFailure exception
    """
    if http_re.match(uri):   # Check for http link
        try:
            with urlopen(uri, timeout=20) as resp:
                if resp.status != 200:
                    raise SourceFailure(f'Got inproper status code({resp.status_code!r}) requesting resource: {resp.url}')
                return resp.read().decode('utf-8')
        except TimeoutError as e:
            raise SourceFailure("Failed to fetch source") from e
    
    else:    # Otherwise thread uri as local file path
        try:
            with open(uri, 'r', encoding='utf-8') as file:
                return file.read()
        except OSError as e:
            raise SourceFailure("Failed to open file") from e



def _build_link_set(src: str) -> Set[str]:
    """Turn given src text into a set of links to trackers
    """
    return {
        i.strip()
        for i in src.splitlines()
        if i and not i.isspace()   # include only non-empty lines
    }


def _fetch_source_links(uri: str) -> Set[str]:
    return _build_link_set(_fetch_list(uri))


def fetch_sources(sources_list: Iterable[str]) -> Set[str]:
    print("----")
    links: Set[str] = set()
    futures_to_url = {pool.submit(_fetch_source_links, i): i for i in sources_list}
    for future in as_completed(futures_to_url):
        url = futures_to_url[future]
        try:
            data = future.result()
        except Exception as e:
            print(f"Error on {url!r}: {e}")
        else:
            print(f"Success: {url!r}, {len(data)} trackers fetched")
            links |= data
    print(f"----\n{len(links)} unique trackers total")
    return links
