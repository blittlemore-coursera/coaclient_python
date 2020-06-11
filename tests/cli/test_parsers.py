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
from argparse import ArgumentParser

from coaclient.cli import RawTextArgsHelpFormatter
from coaclient.cli.parsers import BaseParser, Parser, SubParser


def test_base_parser():
    base_parser = BaseParser()
    # tests type of returned data
    assert isinstance(base_parser.exclude, list)
    assert isinstance(base_parser.asdict(), dict)
    # test method asdict for base parser
    assert base_parser.asdict() == {}


def test_parser():
    parser = Parser()

    assert isinstance(parser.exclude, list)
    assert parser.exclude == ['subparser', 'defaults', 'func', 'args', 'name']

    assert parser.asdict() == {
        'parents': [],
        'formatter_class': RawTextArgsHelpFormatter,
        'prefix_chars': '-',
        'conflict_handler': 'error',
        'add_help': True,
        'allow_abbrev': True
    }

    parser.prog = "Test parser"
    assert (
        'prog' in parser.asdict() and parser.asdict()['prog'] == "Test parser"
    )

    assert parser.subparser is None

    parser.subparser = SubParser()
    assert 'subparser' not in parser.asdict()
    assert isinstance(parser.defaults, dict)
    assert isinstance(parser.args, list)


def test_sub_parser():
    sub_parser = SubParser()

    assert isinstance(sub_parser.exclude, list)
    assert sub_parser.exclude == ['parsers', ]

    assert sub_parser.asdict() == {
        'parser_class': ArgumentParser,
        'required': False
    }

    sub_parser.title = "Test sub parser"
    assert (
        'title' in sub_parser.asdict() and
        sub_parser.asdict()['title'] == "Test sub parser"
    )

    assert isinstance(sub_parser.parsers, list)
    sub_parser.parsers.append(Parser())
    assert 'parsers' not in sub_parser.asdict()
