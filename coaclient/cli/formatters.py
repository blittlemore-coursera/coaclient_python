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
Coaclient Help formatter for CLI factory
"""

from argparse import (
    RawTextHelpFormatter,
    ArgumentDefaultsHelpFormatter
)

__all__ = (
    "RawTextArgsHelpFormatter",
)


class RawTextArgsHelpFormatter(RawTextHelpFormatter,
                               ArgumentDefaultsHelpFormatter):
    """
    RawTextArgsHelpFormatter - Formatter for print help information
    """

    def _format_action_invocation(self, action):
        if not action.option_strings:
            default = self._get_default_metavar_for_positional(action)
            metavar, = self._metavar_formatter(action, default)(1)
            return metavar

        # if the Optional doesn't take a value, format is:
        #    -s, --long
        if action.nargs == 0:
            return ', '.join(action.option_strings)

        # if the Optional takes a value, format is:
        #    -s, --long ARGS
        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return '%s %s' % (
            ', '.join(action.option_strings), args_string
        )
