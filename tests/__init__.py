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
import argparse

from nose.tools import nottest

from coaclient import constants
from coaclient.cli import CLIFactory, Parser, SubParser


@nottest
def empty_cli_factory():
    return CLIFactory(Parser(
        prog=constants.COURSERA_PROG_NAME, subparser=SubParser()
    ))


@nottest
def arguments(**kwargs):
    return argparse.Namespace(**kwargs)
