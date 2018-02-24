Monitor
=======

.. image:: https://travis-ci.org/ReCodEx/monitor.svg?branch=master
   :target: https://travis-ci.org/ReCodEx/monitor

.. image:: http://img.shields.io/:license-mit-blue.svg
   :target: http://badges.mit-license.org

.. image:: https://img.shields.io/badge/docs-wiki-orange.svg
   :target: https://github.com/ReCodEx/wiki/wiki

.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg
   :target: http://recodex.github.io/monitor/

.. image:: https://img.shields.io/github/release/recodex/monitor.svg
   :target: https://github.com/ReCodEx/wiki/wiki/Changelog

Monitor is an optional part of the ReCodEx solution for reporting progress of
job evaluation back to users in the real time. It is a daemon that reads status messages of all running job evaluations from one ZeroMQ socket and send them to proper WebSocket connection. Monitor is written in Python, tested versions are 3.4 and 3.5.

There is just one monitor instance required per broker. Also, monitor has to be
publicly visible (has to have public IP address or be behind public proxy
server) and also needs a connection to the broker. If the web application is
using HTTPS, it is required to use a proxy for monitor to provide encryption
over WebSockets. If this is not done, browsers of the users will block
unencrypted connection and will not show the progress to the users.

Installation
------------

COPR Installation
~~~~~~~~~~~~~~~~~

Follows description for CentOS which will do all steps as described in _Manual Installation_.

.. code::

# yum install yum-plugin-copr
# yum copr enable semai/ReCodEx
# yum install recodex-monitor

Manual Installation
~~~~~~~~~~~~~~~~~~~

For monitor functionality there are some required packages. All of them are
listed in _requirements.txt_ file in the repository and can be installed by
`pip` package manager as

.. code::

$ pip install -r requirements.txt

**Description of dependencies:**

- zmq -- binding to ZeroMQ framework
- websockets -- framework for communication over WebSockets
- asyncio -- library for fast asynchronous operations
- pyyaml -- parsing YAML configuration files
- argparse -- parsing command line arguments

Installation will provide you following files:

- `/usr/bin/recodex-monitor` -- simple startup script located in PATH
- `/etc/recodex/monitor/config.yml` -- configuration file
- `/etc/systemd/system/recodex-monitor.service` -- systemd startup script
- code files will be installed in location depending on your system settings,
  mostly into `/usr/lib/python3.5/site-packages/monitor/` or similar

Systemd script runs monitor binary as specific _recodex_ user, so in `postinst`
script user and group of this name are created. Also, ownership of configuration
file will be granted to that user.

- RPM distributions can make and install binary package. This can be done like
  this:
	- run command

.. code::

$ python3 setup.py bdist_rpm --post-install ./install/postints

	to generate binary `.rpm` package or download precompiled one from releases
	tab of monitor GitHub repository (it is architecture independent package)
	- install package using

.. code::

# yum install ./dist/recodex-monitor-<version>-1.noarch.rpm

- Other Linux distributions can install cleaner straight

.. code::
$ python3 setup.py install --install-scripts /usr/bin
# ./install/postinst


Usage
-----

Preferred way to start monitor as a service is via systemd as the other parts of
ReCodEx solution.

- Running monitor is fairly simple:

.. code::
# systemctl start recodex-monitor.service

- Current state can be obtained by

.. code::
# systemctl status recodex-monitor.service

You should see green **Active (running)**.
- Setting up monitor to be started on system startup:

.. code::
# systemctl enable recodex-monitor.service

Alternatively monitor can be started directly from command line with specifying
path to configuration file. Note that this command will not start monitor as a
daemon.

.. code::
$ recodex-monitor -c /etc/recodex/monitor/config.yml

Or monitor could be executed from within repository like follows:

- run tests by ``python3 monitor/test``
- run app by ``python3 ./main.py -c ./monitor/install/config.yml`` (without specifying configuration file default values will be used)

Configuration
-------------

Configuration file is located in directory `/etc/recodex/monitor/` by default.
It is in YAML format as all of the other configurations.

Configuration items
~~~~~~~~~~~~~~~~~~~

Description of configurable items, bold ones are required, italics ones are
optional.

- _websocket_uri_ -- URI where is the endpoint of WebSocket connection. Must be
  visible to the clients (directly or through public proxy)
	- string representation of IP address or a hostname
	- port number
- _zeromq_uri_ -- URI where is the endpoint of ZeroMQ connection from broker.
  Could be hidden from public internet.
	- string representation of IP address or a hostname
	- port number
- _logger_ -- settings of logging
	- _file_ -- path with name of log file. Defaults to
	  `/var/log/recodex/monitor.log`
	- _level_ -- logging level, one of "debug", "info", "warning", "error" and
	  "critical"
	- _max-size_ -- maximum size of log file before rotation in bytes
	- _rotations_ -- number of rotations kept

Example configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: yaml
---
websocket_uri:
    - "127.0.0.1"
    - 4567
zeromq_uri:
    - "127.0.0.1"
    - 7894
logger:
    file: "/var/log/recodex/monitor.log"
    level: "debug"
    max-size: 1048576  # 1 MB
    rotations: 3
...

Documentation
-------------

Feel free to read the documentation on [our wiki](https://github.com/ReCodEx/wiki/wiki).
