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
Coaclient Parsers description for CLI factory
"""

from argparse import ArgumentParser, HelpFormatter
from dataclasses import dataclass, field, asdict
from typing import (
    Optional,
    List, Dict, Any
)

from coaclient.cli.formatters import RawTextArgsHelpFormatter

__all__ = (
    "Parser",
    "SubParser",
    "BaseParser"
)


@dataclass
class BaseParser:
    """
    BaseParser - base parser description class
    """

    @property
    def exclude(self) -> list:
        """
        Get a list of excluded attributes for converting instance to
        the dictionary.
        """
        return list()

    def asdict(
            self,
            exclude: Optional[List[str]] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Convert instance to the dictionary

        :param: exclude - list of excluded attributes (optional). Extended
                          base list of excluded attributes.
        :return: Dict   - dictionary, where the key is the name of instance
                          attributes and value, is the value of these
                          attributes
        """
        if exclude is None:
            exclude = []
        exclude.extend(self.exclude)
        return {
            key: kwargs.get(key, value)
            for key, value in asdict(self).items()
            if (value is not None or key in kwargs) and key not in self.exclude
        }


@dataclass
class Parser(BaseParser):
    """
    Parser - Parsers description class for cli

    +-----------------------+-------------------------------------------------+
    | Parameter             | Description                                     |
    +-----------------------+-------------------------------------------------+
    | prog                  | The name of the program (default: sys.argv[0])  |
    +-----------------------+-------------------------------------------------+
    | usage                 | The string describing the program usage         |
    |                       | (default: generated from arguments added to     |
    |                       |  parser)                                        |
    +-----------------------+-------------------------------------------------+
    | description           | Text to display before the argument help        |
    |                       | (default: none)                                 |
    +-----------------------+-------------------------------------------------+
    | epilog                | Text to display after the argument help         |
    |                       | (default: none)                                 |
    +-----------------------+-------------------------------------------------+
    | parents               | A list of ArgumentParser objects whose          |
    |                       | arguments should also be included               |
    +-----------------------+-------------------------------------------------+
    | formatter_class       | A class for customizing the help output         |
    +-----------------------+-------------------------------------------------+
    | prefix_chars          | The set of characters that prefix optional      |
    |                       | arguments (default: ‘-‘)                        |
    +-----------------------+-------------------------------------------------+
    | fromfile_prefix_chars | The set of characters that prefix files from    |
    |                       | which additional arguments should be read       |
    |                       | (default: None)                                 |
    +-----------------------+-------------------------------------------------+
    | argument_default      | The global default value for arguments          |
    |                       | (default: None)                                 |
    +-----------------------+-------------------------------------------------+
    | conflict_handler      | The strategy for resolving conflicting          |
    |                       | optionals (usually unnecessary)                 |
    +-----------------------+-------------------------------------------------+
    | add_help              | Add a -h/--help option to the parser            |
    |                       | (default: True)                                 |
    +-----------------------+-------------------------------------------------+
    | allow_abbrev          | Allows long options to be abbreviated if the    |
    |                       | abbreviation is unambiguous. (default: True)    |
    +-----------------------+-------------------------------------------------+
    """
    # _pylint: disable=too-many-instance-attributes
    # Disable this warning for dataclass or we can set the value of the
    # `max-attributes` field to more than 7 in the .pylintrc file
    # (` max-attributes` is 7 by default).
    name: Optional[str] = None
    prog: Optional[str] = None
    usage: Optional[str] = None
    description: Optional[str] = None
    epilog: Optional[str] = None
    parents: List[ArgumentParser] = field(default_factory=list)
    formatter_class: HelpFormatter = RawTextArgsHelpFormatter
    prefix_chars: str = '-'
    fromfile_prefix_chars: Optional[str] = None
    argument_default: Optional[str] = None
    conflict_handler: str = 'error'
    add_help: bool = True
    allow_abbrev: bool = True
    help: Optional[str] = None
    subparser: Optional['SubParser'] = None
    defaults: Dict[str, Any] = field(default_factory=dict)
    func: Optional[object] = None
    args: List[str] = field(default_factory=list)

    @property
    def exclude(self) -> list:
        """
        Get a list of excluded attributes in the Parser class for converting
        that instance to the dictionary.
        """
        return ['subparser', 'defaults', 'func', 'args', 'name']


@dataclass
class SubParser(BaseParser):
    """
    SubParser - Subparsers description class for cli

    +--------------+----------------------------------------------------------+
    | Parameter    | Description                                              |
    +--------------+----------------------------------------------------------+
    | title        | title for the sub-cli group in help output; by           |
    |              | default “subcommands” if description is provided,        |
    |              | otherwise uses title for positional arguments            |
    +--------------+----------------------------------------------------------+
    | description  | description for the sub-cli group in help output,        |
    |              | by default None                                          |
    +--------------+----------------------------------------------------------+
    | prog         | usage information that will be displayed with            |
    |              | sub-command help, by default the name of the program     |
    |              | and any positional arguments before the subparser        |
    |              | argument                                                 |
    +--------------+----------------------------------------------------------+
    | parser_class | class which will be used to create sub-cli               |
    |              | instances, by default the class of the current cli       |
    |              | (e.g. ArgumentParser)                                    |
    +--------------+----------------------------------------------------------+
    | action       | the basic type of action to be taken when this argument  |
    |              | is encountered at the command line                       |
    +--------------+----------------------------------------------------------+
    | dest         | name of the attribute under which sub-command name       |
    |              | will be stored; by default None and no value is stored   |
    +--------------+----------------------------------------------------------+
    | required     | Whether or not a subcommand must be provided,            |
    |              | by default False.                                        |
    +--------------+----------------------------------------------------------+
    | help         | help for sub-cli group in help output,                   |
    |              | by default None                                          |
    +--------------+----------------------------------------------------------+
    | metavar      | string presenting available sub-commands in help;        |
    |              | by default it is None and presents sub-commands          |
    |              | in form {cmd1, cmd2, ..}                                 |
    +--------------+----------------------------------------------------------+
    """
    # _pylint: disable=too-many-instance-attributes
    # Disable this warning for dataclass or we can set the value of the
    # `max-attributes` field to more than 7 in the .pylintrc file
    # (` max-attributes` is 7 by default).
    title: Optional[str] = None
    description: Optional[str] = None
    prog: Optional[str] = None
    parser_class: ArgumentParser = ArgumentParser
    action: Optional[str] = None
    dest: Optional[str] = None
    required: Optional[bool] = False
    help: Optional[str] = None
    metavar: Optional[str] = None
    parsers: List['Parser'] = field(default_factory=list)

    @property
    def exclude(self):
        """
        Get a list of excluded attributes in the SubParser class for
        converting that instance to the dictionary.
        """
        return ['parsers', ]
