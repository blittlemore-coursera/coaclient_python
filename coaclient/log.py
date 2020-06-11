# Copyright 2020 Coursera
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Coaclient log module
"""
import logging as _logging

import urllib3

from coaclient import constants
from coaclient.cli import Arg, Actions


__all__ = (
    "add_logging",
    "LogLevels",
)


class LogLevels:
    """ Available levels of logging for coaclient """
    INFO = _logging.INFO
    DEBUG = _logging.DEBUG
    WARNING = _logging.WARNING
    ERROR = _logging.ERROR
    CRITICAL = _logging.CRITICAL
    LEVELS = [INFO, WARNING, ERROR, DEBUG, CRITICAL]

    @staticmethod
    def get_level_name(level):
        """
        Getting level name by level id or getting level id by level name
        """
        return _logging.getLevelName(level)

    @classmethod
    def log_levels(cls):
        """ Getting all available levels for logging """
        return [
            _logging.getLevelName(name) for name in cls.LEVELS
        ]


def add_logging(cli):
    """
    Add setup logging method to cli arguments methods
    Add additional arguments for logging configuration

    1. -l, --loglevel       Argument for setup loglevel for logger
                            Default: INFO
    2. --silence-urllib3    Argument which tell us should we show silence
                            urllib3 warnings or no.
    """
    cli.parser.defaults.update(setup_logging=setup_logging)
    # Add additional arguments for logging configuration
    cli.add_arguments(log_level=Arg(
        flags=('-l', '--log-level'),
        default=LogLevels.get_level_name(LogLevels.INFO),
        choices=LogLevels.log_levels(),
        help=constants.COURSERA_LOG_LEVEL_HELP
    ), silence_urllib3=Arg(
        flags=('--silence-urllib3',),
        action=Actions.STORE_TRUE,
        help=constants.COURSERA_LOG_SILENCE_URLLIB3
    ))
    # Setup these args as global for cli
    cli.parser.args.extend(['log_level', 'silence_urllib3'])


def setup_logging(args):
    """
    Computes and sets the logging configuration from the parsed arguments.
    """
    # Set CLI log format
    _logging.basicConfig(format="coaclient: %(message)s")
    # Get main logger
    logger = _logging.getLogger()
    # Setup log level for logger
    logger.setLevel(LogLevels.get_level_name(args.log_level))

    # Setup log level for urllib3 package logger
    _logging.getLogger("requests.packages.urllib3").setLevel(
        LogLevels.WARNING
    )
    if args.silence_urllib3 is True:
        # For details see:
        # https://urllib3.readthedocs.org/en/latest/security.html
        urllib3.disable_warnings()
