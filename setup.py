#!/usr/bin/env python
from setuptools import setup

from add_free_announcers import __version__


setup(name='add_free_announcers',
      version=__version__,
      description='Add free announcers to torrent files',
      author='cmd410, belibak, Vftdan',
      url='https://github.com/cmd410/add-free-announcers',
      packages=['add_announcers'],
      entry_points={
          'console_scripts': [
                'add-free-announcers = add_announcers:main',
            ]
      }
)