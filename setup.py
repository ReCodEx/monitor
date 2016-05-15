#!/usr/bin/env python3

from setuptools import setup
from monitor import __version__


setup(name='recodex-monitor',
      version=__version__,
      description='Publish ZeroMQ messages through WebSockets',
      author='Petr Stefan',
      author_email='',
      url='https://github.com/ReCodEx/monitor',
      license="MIT",
      keywords=['ReCodEx', 'messages', 'ZeroMQ', 'WebSockets'],
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   'Operating System :: POSIX :: Linux',
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.4",
                   "Programming Language :: Python :: 3.5"],
      packages=['monitor'],
      package_data={'': ['../install/*']},
      data_files=[
          ('/etc/systemd/system', ['install/recodex-monitor.service']),
          ('/etc/recodex/monitor', ['install/config.yml'])
          ],
      entry_points={'console_scripts': ['recodex-monitor = monitor.main:main']}
      )
