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
Coaclient Args description for CLI factory
"""

from dataclasses import dataclass
from typing import (
    Tuple,
    Union,
    Text,
    Any,
    Type,
    List,
    Optional
)

__all__ = (
    "Actions", "Arg"
)


class Actions:
    """ Actions for cli """
    # _pylint: disable=too-few-public-methods
    # Disable this warning because that is a static class or
    # we can provide .pylintrc file where will
    # setup `min-public-methods` less than 2
    # (`min-public-methods=2` uses by pylint as default).
    STORE: str = 'store'
    STORE_CONST: str = 'store_const'
    STORE_TRUE: str = 'store_true'
    STORE_FALSE: str = 'store_false'
    APPEND: str = 'append'
    APPEND_CONST: str = 'append_const'
    COUNT: str = 'count'
    VERSION: str = 'version'
    HELP: str = 'help'


@dataclass
class Arg:
    """
    Arg - Argument description class for cli

    +-----------+-------------------------------------------------------------+
    | Parameter | Description                                                 |
    +-----------+-------------------------------------------------------------+
    | flags     | Either a name or a list of option strings, e.g. foo or      |
    |           | -f, --foo.                                                  |
    +-----------+-------------------------------------------------------------+
    | action    | The basic type of action to be taken when this argument is  |
    |           | encountered at the command line.                            |
    +-----------+-------------------------------------------------------------+
    | nargs     | The number of command-line arguments that should be         |
    |           | consumed.                                                   |
    +-----------+-------------------------------------------------------------+
    | const     | A constant value required by some action and nargs          |
    |           | selections.                                                 |
    +-----------+-------------------------------------------------------------+
    | default   | The value produced if the argument is absent from the       |
    |           | command line.                                               |
    +-----------+-------------------------------------------------------------+
    | type      | The type to which the command-line argument should be       |
    |           | converted.                                                  |
    +-----------+-------------------------------------------------------------+
    | choices   | A container of the allowable values for the argument.       |
    +-----------+-------------------------------------------------------------+
    | required  | Whether or not the command-line option may be omitted       |
    |           | (optionals only).                                           |
    +-----------+-------------------------------------------------------------+
    | help      | A brief description of what the argument does.              |
    +-----------+-------------------------------------------------------------+
    | metavar   | A name for the argument in usage messages.                  |
    +-----------+-------------------------------------------------------------+
    | dest      | The name of the attribute to be added to the object         |
    |           | returned by parse_args().                                   |
    +-----------+-------------------------------------------------------------+
    """
    # _pylint: disable=too-many-instance-attributes
    # Disable this warning for dataclass or we can set the value of the
    # `max-attributes` field to more than 7 in the .pylintrc file
    # (` max-attributes` is 7 by default).

    flags: Union[Tuple, str]
    help: Text = ""
    action: str = Actions.STORE
    default: Any = None
    type: Optional[Type] = None
    choices: Optional[List[Any]] = None
    metavar: Optional[str] = None
    nargs: Optional[Union[int, str]] = None
    const: Optional[Any] = None
    required: bool = False
    dest: Optional[str] = None
