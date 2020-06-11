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
Coursera OAuth2 client command

Command: version
"""

import sys

from coaclient import __version__
from coaclient.cli import Parser

from coaclient.log import LogLevels

__all__ = (
    "add_command",
)

_LOGS_LEVELS = [
    LogLevels.get_level_name(LogLevels.WARNING),
    LogLevels.get_level_name(LogLevels.ERROR)
]


def version(args):
    """
    Output the application version
    """
    msg = "Your {prog}'s version is: {version}s".format(
        prog=sys.argv[0].split('/')[-1], version=__version__
    )
    if args.log_level in _LOGS_LEVELS:
        msg = __version__
    print(msg)


def add_command(cli_factory):
    """
    Create version command with command handler and add to the Coursera's CLI
    """
    cli_factory.parser.subparser.parsers.append(Parser(
        name="version",
        help="Output the version %(prog)s.",
        func=version
    ))
