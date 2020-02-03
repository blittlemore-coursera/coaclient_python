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
Coursera's OAuth2 client

You may install it from source, or via pip.
"""

import logging
import urllib3


LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'TRACE': 5  # TRACE level
}


def add_logging_parser(main_parser):
    "Build an argparse argument parser to parse the command line."

    main_parser.set_defaults(setup_logging=set_logging_level)

    main_parser.add_argument(
        '--loglevel',
        '-l',
        default='INFO',
        choices=['INFO', 'DEBUG', 'WARNING', 'ERROR', 'TRACE']
    )

    main_parser.add_argument(
        '--silence-urllib3',
        action='store_true',
        help=(
            'Silence urllib3 warnings. See '
            'https://urllib3.readthedocs.org/en/latest/security.html '
            'for details.'
        )
    )


def set_logging_level(args):
    """Computes and sets the logging level from the parsed arguments."""
    root_logger = logging.getLogger()
    logging.getLogger('requests.packages.urllib3').setLevel(logging.WARNING)
    log_level = args.loglevel
    level = LOG_LEVELS.get(log_level, logging.INFO)

    root_logger.setLevel(level)

    if args.silence_urllib3:
        # See: https://urllib3.readthedocs.org/en/latest/security.html
        urllib3.disable_warnings()


def validate_not_empty_input(input_message):
    """Validate input for empty value"""
    while True:
        value = input(input_message)
        if len(value.strip()) < 1:
            print("Value can't be empty")
        else:
            break

    return value
