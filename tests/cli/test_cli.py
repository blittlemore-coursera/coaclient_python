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
from argparse import ArgumentParser, _StoreAction

from coaclient.cli import Parser, SubParser, CLIFactory, Arg


def test_cli_factory_setup_arguments():
    parser_config = Parser(subparser=SubParser())

    cli_factory = CLIFactory(parser=parser_config)
    assert cli_factory.parser == parser_config

    cli_factory.add_arguments(
        config=Arg(
            flags=('-c', '--config'),
            type=str,
            help="Path to your custom the configuration file to use."
        ),
        empty=None
    )
    parser = ArgumentParser(**cli_factory.parser.asdict())
    cli_factory._setup_arguments(parser, ['config', 'empty'])
    assert len(parser._actions) == 2
    assert isinstance(parser._actions[1], _StoreAction)
    assert parser._actions[1].option_strings == ['-c', '--config']


def test_cli_factory_setup_subparsers():
    def subcommand(args):
        return "Test handler for subcommand"

    parser_config = Parser(subparser=SubParser(
        title="Test subparser"
    ))
    cli_factory = CLIFactory(parser=parser_config)
    cli_factory.parser.subparser.parsers.append(Parser(
        name="subcommand",
        help="Help text for subcommand.",
        func=subcommand,
        defaults={
            "subcommand": subcommand
        },
        subparser=SubParser(parsers=[Parser(name="helper", func=None), ])
    ))


    parser = ArgumentParser(**cli_factory.parser.asdict())
    assert parser._subparsers is None
    cli_factory._setup_subparsers(parser, cli_factory.parser)
    assert parser._subparsers is not None
    assert parser._subparsers.title == "Test subparser"


def test_cli_factory_get_cli():
    def subcommand(args):
        return "Test handler for subcommand"

    parser_config = Parser(subparser=SubParser(
        title="Test subparser"
    ), defaults={
        "subcommand": subcommand
    })
    cli_factory = CLIFactory(parser=parser_config)
    cli_factory.parser.subparser.parsers.append(Parser(
        name="subcommand",
        help="Help text for subcommand.",
        func=subcommand,
        defaults={
            "subcommand": subcommand
        },
        subparser=SubParser(parsers=[Parser(name="helper", func=None), ])
    ))

    parser = cli_factory.get_cli()
    assert isinstance(parser, ArgumentParser)
