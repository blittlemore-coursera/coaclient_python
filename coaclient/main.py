#!/usr/bin/env python

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
Coursera's OAuth2 client library.

You may install it from source, or via pip.
"""

import argparse
import logging
import sys

from coaclient import commands
from coaclient import utils


def build_parser():
    """Build an argparse argument parser to parse the command line."""
    parser = argparse.ArgumentParser(
        description="""Coursera OAuth2 client CLI. This tool
        helps users of the Coursera App Platform to programmatically access
        Coursera APIs.""",
        epilog="""Please file bugs on github at:
        https://github.com/blittlemore-coursera/coaclient/issues
        If you
        would like to contribute to this tool's development, check us out at:
        https://github.com/blittlemore-coursera/coaclient
        """)
    parser.add_argument('-c', '--config', help='the configuration file to use')
    utils.add_logging_parser(parser)

    # We support multiple subcommands. These subcommands have their own
    # subparsers. Each subcommand should set a default value for the 'func'
    # option. We then call the parsed 'func' function, and execution carries on
    # from there.
    subparsers = parser.add_subparsers()

    commands.config.parser(subparsers)
    commands.version.parser(subparsers)

    return parser


def main():
    """Boots up the command line tool"""
    logging.captureWarnings(True)
    parser = build_parser()
    args = parser.parse_args()
    # Configure logging
    args.setup_logging(args)
    # Dispatch into the appropriate subcommand function.
    try:
        return args.func(args)
    except AttributeError:
        parser.print_help()
        parser.exit()
    except:
        logging.exception('There were problems running the command.')
        sys.exit(1)


if __name__ == "__main__":
    main()
