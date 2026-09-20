# Monitor

[![CI](https://github.com/ReCodEx/monitor/workflows/CI/badge.svg)](https://github.com/ReCodEx/monitor/actions)
[![License: MIT](http://img.shields.io/:license-mit-blue.svg)](http://badges.mit-license.org)
[![Documentation: wiki](https://img.shields.io/badge/docs-wiki-orange.svg)](https://github.com/ReCodEx/wiki/wiki)
[![Documentation: latest](https://img.shields.io/badge/docs-latest-brightgreen.svg)](http://recodex.github.io/monitor/)
[![Release](https://img.shields.io/github/release/recodex/monitor.svg)](https://github.com/ReCodEx/wiki/wiki/Changelog)

Monitor is an optional part of the ReCodEx solution for reporting the progress
of job evaluation to users in real time. It is a daemon that reads status
messages from all running job evaluations through a ZeroMQ socket and sends
them to the appropriate WebSocket connection. Monitor is written in Python
(>= 3.9).

Only one monitor instance is required per broker. Monitor must be publicly
visible (it must have a public IP address or be behind a public proxy server)
and must also be connected to the broker. If the web application uses HTTPS,
the monitor must be behind a proxy that provides encryption over WebSockets.
Otherwise, users' browsers will block the unencrypted connection and will not
show job progress.

## Installation

### COPR installation (recommended)

For RHEL-like systems, the easiest way is to install the monitor from the COPR repository as an RPM package:

```
# dnf install dnf-plugin-copr
# dnf copr enable semai/ReCodEx
# dnf install recodex-monitor
```

For other systems, please follow the manual installation instructions below.


### Manual Installation

The monitor requires the packages listed in `requirements.txt`, and you also need build tools for manual installation. Install them using `pip`:

```
$ pip install -r requirements.txt
$ pip install build setuptools wheel
```

Or in managed environments like in Debian:
```
# apt install python3-build python3-setuptools python3-wheel python3-zmq python3-websockets python3-yaml
```

The monitor can be installed with the following command:

```
# pip3 install --global .
```

In the case of Debian-based systems, you may need to add `--break-system-packages`, or use `pipx` instead of `pip` to avoid breaking system packages (install it by `apt install pipx` first).

Afterwards, you need to run the post-installation script manually. It will copy the configuration file to `/etc/recodex/monitor/config.yml`, create the `recodex` user and group, and prepare the `/var/log/recodex` directory for logs:
```
./monitor/install/postinst
```

Finally, you need to copy the systemd service file `./monitor/install/recodex-monitor.service` to `/etc/systemd/system/recodex-monitor.service` and reload the systemd daemon:
```
# systemctl daemon-reload
```
If the monitor is not installed in `/usr/bin/recodex-monitor`, create either a symlink or update the `ExecStart` line in the systemd service file to point to the correct location of the monitor binary.


## Usage

The preferred way to run monitor is as a systemd service, as with other parts of the ReCodEx solution. After properly updating the configuration file in `/etc/recodex/monitor/config.yml`, you may start the service:

```
# systemctl start recodex-monitor
```

Obtain its current state (verify that it is running) with:

```
# systemctl status recodex-monitor
```

And to permanently enable the service to start on boot, run:

```
# systemctl enable recodex-monitor
```

Alternatively, start monitor directly from the command line by specifying the configuration file path. This command does not start monitor as a daemon. This is useful for testing and debugging purposes.

```
$ recodex-monitor -c /etc/recodex/monitor/config.yml
```

You can also run monitor from within the repository (useful for development purposes):

- Run tests with `python3 monitor/test`.
- Run the application with `python3 ./main.py -c ./monitor/install/config.yml`. If no configuration file is specified, default values are used.


## Configuration

The configuration file is located in `/etc/recodex/monitor/config.yaml` by default. It uses the YAML format, as do the other ReCodEx configurations.

Required items are in bold; optional items are in italics.

- **`websocket_uri`**: URI of the WebSocket endpoint. It must be visible to clients, either directly or through a public proxy.
  - String representation of an IP address or hostname
  - Port number
- **`zeromq_uri`**: URI of the ZeroMQ endpoint connected to the broker. It may (should) be hidden from the public internet.
  - String representation of an IP address or hostname
  - Port number
- **`logger`**: logging settings
  - *`file`*: path and filename of the log file. Defaults to
    `/var/log/recodex/monitor.log`
  - *`level`*: logging level; one of `debug`, `info`, `warning`, `error`, or `critical`
  - *`max-size`*: maximum log file size in bytes before rotation
  - *`rotations`*: number of retained log rotations


**Example:**

```yaml
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
    max-size: 1048576 # 1 MB
    rotations: 3
...
```

Assuming the frontend web-server has appropriate proxy settings to forward WebSocket connections to the monitor. In the case of Apache, the following configuration line can be used:

```
ProxyPass "/ws" "ws://127.0.0.1:4567"
```
