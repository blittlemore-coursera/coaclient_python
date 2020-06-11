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
Coaclient CLI factory description
"""

from argparse import ArgumentParser
from dataclasses import asdict
from typing import List, Optional

from .args import Arg
from .parsers import Parser


class CLIFactory:
    """
    CLI Factory - factory for build CLI
    """

    def __init__(
            self,
            parser,
            *,
            args=None
    ):
        self._parser = parser
        self._args = args or {}

    @property
    def parser(self) -> Parser:
        """
        Get Parser description instance that uses as the main parser in CLI
        factory.
        """
        return self._parser

    def add_arguments(self, **args: Optional[Arg]) -> None:
        """
        Add arguments description to CLI factory which uses for the main
        parser and subparsers.
        """
        for arg_name, arg_conf in args.items():
            self._args[arg_name] = arg_conf

    def _setup_arguments(
            self,
            parser: ArgumentParser,
            args: List[str]
    ) -> None:
        for arg_name in args:
            arg_config = self._args.get(arg_name)
            if arg_config is None:
                continue
            kwargs = {}
            for field, value in asdict(arg_config).items():
                if field != "flags" and value is not None:
                    kwargs[field] = value
            parser.add_argument(*arg_config.flags, **kwargs)

    def _setup_subparsers(
            self,
            parser: ArgumentParser,
            parser_config: Parser
    ) -> None:
        subparsers = parser.add_subparsers(**parser_config.subparser.asdict())
        for p_config in parser_config.subparser.parsers:
            # Create sub parser
            _parser = subparsers.add_parser(p_config.name, **p_config.asdict(
                epilog=parser.epilog, description=parser.description
            ))
            # Setup parser arguments
            self._setup_arguments(_parser, p_config.args)
            # Setup default handler
            if p_config.func is not None:
                _parser.set_defaults(func=p_config.func)
            # Setup defaults
            if p_config.defaults:
                _parser.set_defaults(**p_config.defaults)
            # Setup subparsers
            if p_config.subparser is not None:
                self._setup_subparsers(_parser, p_config)

    def get_cli(self, *, args=None, **kwargs):
        """
        Build and return the main CLI parser.
        """
        # Create main parser
        parser = ArgumentParser(**self.parser.asdict(**kwargs))
        # Extend main parser args if provided
        self.parser.args.extend(args or [])
        # Setup arguments for main parser
        self._setup_arguments(parser, self.parser.args)
        # Setup defaults for main parser
        if self.parser.defaults:
            parser.set_defaults(**self.parser.defaults)

        if self.parser.subparser is not None:
            # Setup subparsers
            self._setup_subparsers(parser, self.parser)

        return parser
