Monitor
=======

.. image:: https://travis-ci.org/ReCodEx/monitor.svg?branch=master
    :target: https://travis-ci.org/ReCodEx/monitor

.. image:: http://img.shields.io/:license-mit-blue.svg
   :target: http://badges.mit-license.org

.. image:: https://img.shields.io/badge/docs-wiki-orange.svg
   :target: https://github.com/ReCodEx/GlobalWiki/wiki

.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg
   :target: http://recodex.github.io/monitor/

A daemon that reads status messages of all running job evaluations from one ZeroMQ socket and send them to proper WebSocket connection.


How to run it
-------------

- install ``python3`` and ``pip`` according to your OS
- install dependencies executing ``pip install -r requirements.txt``
- run tests by ``python3 monitor/test``
- run app by ``python3 monitor/main.py -c ./install/config.yml`` (without specifying configuration file default values will be used)


Installation
------------

**Fedora (and other RPM distributions):**

- run ``python3 setup.py bdist_rpm --post-install ./install/postints`` to generate binary ``.rpm`` package **or** download it from releases tab
- install package using ``sudo dnf install ./dist/recodex-monitor-0.1.0-1.noarch.rpm`` (depends on actual version)

**Other Linux systems:**

- run installation as ``python3 setup.py install``
- run postinst script as root -  ``sudo ./install/postinst``


Configuration and running
-------------------------

- edit configuration file ``/etc/recodex/monitor/config.yml``
- run as systemd service via ``sudo systemctl start recodex-monitor.service`` **or** from command line as ``recodex-monitor -c /etc/recodex/monitor/config.yml``

