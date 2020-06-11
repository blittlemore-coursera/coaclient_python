#!/usr/bin/env python3

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
"""
import logging

from coaclient import (
    commands, constants
)
from coaclient.cli import (
    CLIFactory, Arg, Parser, SubParser
)
from coaclient.commands.exceptions import CoaClientCommandException
from coaclient.log import add_logging
from coaclient.oauth2.exceptions import (
    OAuth2ClientException,
    OAuth2ConfigError,
    OAuth2CacheException,
    OAuth2TokenExpiredError
)


def build_cli():
    """
    Build CLI for use Coursera OAuth2.0 client library

    return: CLIParser
    """
    cli_factory = CLIFactory(Parser(
        prog=constants.COURSERA_PROG_NAME, subparser=SubParser()
    ))
    # Initialize main used arguments
    cli_factory.add_arguments(
        config=Arg(
            flags=('-c', '--config'),
            type=str,
            help="Path to your custom the configuration file to use."
        )
    )
    cli_factory.parser.args.append('config')
    # Add logging configuration to Coursera CLI
    add_logging(cli_factory)

    # Add CLI commands
    commands.version.add_command(cli_factory)
    commands.config.add_command(cli_factory)

    return cli_factory.get_cli(
        description=constants.COURSERA_CLI_DESCRIPTION,
        epilog=constants.COURSERA_CLI_EPILOG
    )


def main():
    """
    Creating and initializing the CLI for processing input operations
    """
    cli = build_cli()
    args = cli.parse_args()
    # Configure logging
    args.setup_logging(args)
    logging.debug("[!!! DANGER !!!] Please do not use DEBUG mode for the "
                  "log file in production. Do it only on you own risk. "
                  "[!!! DANGER !!!]")

    status, message = 0, ""
    try:
        args.func(args)
    except AttributeError:
        status, message = (
            1, "Sub-command didn't set for processing your operation. "
               "Please see in `coaclient --help` how to use coaclient.\n"
        )
    except (
            CoaClientCommandException,
            OAuth2ClientException,
            OAuth2ConfigError,
            OAuth2CacheException,
            OAuth2TokenExpiredError
    ) as err:
        status, message = (1, "{err}\n".format(err=str(err)))
    finally:
        cli.exit(status, message)


if __name__ == "__main__":
    main()
