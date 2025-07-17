#!/usr/bin/env python3

import yaml
import logging
import logging.handlers


class ConfigManager:
    """
    Class to handle all configuration items.
    """
    def __init__(self, config_file=None):
        """
        Init with default values.

        :param config_file: Path to YAML configuration file.
            If not given, default values are used.
        """

        self._config = dict()
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    self._config = yaml.safe_load(f)
            except FileNotFoundError:
                # using defaults
                pass

    def get_websocket_uri(self):
        """
        Get address for websocket server.

        :return: List with 2 items - string hostname and int port
        """
        return self._config['websocket_uri'] if 'websocket_uri' in self._config else ['127.0.0.1', 4567]

    def get_zeromq_uri(self):
        """
        Get address for zeromq server.

        :return: List with 2 items - string hostname and int port
        """
        return self._config['zeromq_uri'] if 'zeromq_uri' in self._config else ['127.0.0.1', 7894]

    def get_logger_settings(self):
        """
        Get path to system log file.

        :return: List with 4 items - string path, logging level, integer maximum size
            of logfile and integer number of rotations kept.
        """
        result = ["/tmp/recodex-monitor.log", logging.INFO, 1024*1024, 3]
        if 'logger' in self._config:
            sect = self._config['logger']
            if 'file' in sect:
                result[0] = sect['file']
            if 'level' in sect:
                result[1] = self._get_loglevel_from_string(sect['level'])
            if 'max-size' in sect:
                try:
                    result[2] = int(sect['max-size'])
                except:
                    pass
            if 'rotations' in sect:
                try:
                    result[3] = int(sect['rotations'])
                except:
                    pass
        return result

    def _get_loglevel_from_string(self, str_level):
        """
        Convert logging level from string to logging module type.

        :param str_level: string representation of logging level
        :return: logging level (defaults to logging.INFO)
        """
        level_mapping = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }
        if str_level in level_mapping:
            return level_mapping[str_level]
        else:
            return logging.INFO


def init_logger(logfile, level, max_size, rotations):
    """
    Initialize new system logger for monitor. If arguments are invalid,
    empty logger will be created.

    :param logfile: Path to file with log.
    :param level: Log level as logging.<LEVEL>
    :param max_size: Maximum size of log file.
    :param rotations: Number of log files kept.
    :return: Initialized logger.
    """
    try:
        # create logger
        logger = logging.getLogger('recodex-monitor')
        logger.setLevel(level)

        # create rotating file handler
        ch = logging.handlers.RotatingFileHandler(logfile, maxBytes=max_size, backupCount=rotations)
        ch.setLevel(level)

        # create formatter
        formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)
    except Exception as e:
        # create empty logger
        print("Invalid logger configuration. Creating null logger. Error: {}".format(e))
        logger = logging.getLogger('recodex-monitor-dummy')
        logging.disable(logging.CRITICAL)

    # print welcome message to log file
    logger.critical("-------------------------")
    logger.critical(" ReCodEx Monitor started")
    logger.critical("-------------------------")

    # return created logger
    return logger
