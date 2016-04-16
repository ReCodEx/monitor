#!/usr/bin/env python

from setuptools import setup

from monitor import __version__


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='monitor',
      version=__version__,
      description='Publish ZeroMQ messages through WebSockets',
      long_description=readme(),
      author='Petr Stefan',
      author_email='',
      url='https://github.com/ReCodEx/monitor',
      license="MIT",
      keywords=['ReCodEx', 'messages', 'ZeroMQ', 'WebSockets'],
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.4"],
      packages=['monitor'],
      entry_points={'console_scripts': ['recodex-monitor = monitor.main:main']})
