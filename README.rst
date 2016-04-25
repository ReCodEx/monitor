Monitor
=======

.. image:: https://travis-ci.org/ReCodEx/monitor.svg?branch=master
    :target: https://travis-ci.org/ReCodEx/monitor

.. image:: http://img.shields.io/:license-mit-blue.svg
   :target: http://badges.mit-license.org

.. image:: https://img.shields.io/badge/docs-wiki-orange.svg
   :target: https://github.com/ReCodEx/GlobalWiki/wiki


A daemon that reads status messages of all running job evaluations from one ZeroMQ socket and send them to proper WebSocket connection.

How to run it
-------------

- install ``python3`` and ``pip`` according to your OS
- install dependencies executing ``pip install -r requirements.txt``
- run tests by ``python3 monitor/test``
- run app by ``python3 main.py -c ./config.yml`` (without specifying configuration file default values will be used)

