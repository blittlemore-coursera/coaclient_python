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
Coaclient constants for CLI
"""

__all__ = (
    "COURSERA_PROG_NAME",
    "COURSERA_CLI_DESCRIPTION",
    "COURSERA_CLI_EPILOG",
    "COURSERA_LOG_LEVEL_HELP",
    "COURSERA_LOG_SILENCE_URLLIB3"
)

# Courser main cli constants
COURSERA_PROG_NAME = "coaclient"
COURSERA_CLI_DESCRIPTION = (
    "Coursera OAuth2 client CLI.\nThis tool helps users of the Coursera App "
    "Platform to programmatically access Coursera APIs."
)
COURSERA_CLI_EPILOG = (
    "Please file bugs on github at: "
    "https://github.com/blittlemore-coursera/coaclient/issues\n"
    "If you would like to contribute to this tool's development, "
    "check us out at: https://github.com/blittlemore-coursera/coaclient"
)

# Coursera logging constants
COURSERA_LOG_LEVEL_HELP = (
    "Used for setup log level for output messages.\n"
    "By default the log level is INFO."
)
COURSERA_LOG_SILENCE_URLLIB3 = (
    'Silence urllib3 warnings.\n'
    'See https://urllib3.readthedocs.org/en/latest/security.html for details.'
)
