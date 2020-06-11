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
Coursera OAuth2.0 client library
"""
import os
from configparser import ConfigParser
from typing import Optional

from .settings import (
    OAUTH2_CONFIG_PATH,
    OAUTH2_CONFIG_FILE_NAME,
    OAUTH2_HOSTNAME,
    OAUTH2_PORT,
    OAUTH2_API_ENDPOINT,
    OAUTH2_AUTH_ENDPOINT,
    OAUTH2_TOKEN_ENDPOINT,
    OAUTH2_VERIFY_TLS,
    OAUTH2_TOKEN_CACHE_PATH,
)
from .utils import make_or_check_dir


class Config(ConfigParser):
    """ Configuration Coursera OAuth2.0 class """
    # _pylint: disable=too-many-ancestors
    # Disable this warning for Config or we can set the value of the
    # `max-parents` field to more than 7 in the .pylintrc file
    # (`max-parents` is 7 by default).
    OAUTH2_SECTION = "OAuth2"
    _FILE_PATH = os.path.join(
        OAUTH2_CONFIG_PATH, OAUTH2_CONFIG_FILE_NAME
    )

    @classmethod
    def load_from_file(cls, filename: Optional[str] = None):
        """
        Load configuration from file
        """
        config = cls()
        if filename is None:
            filename = cls._FILE_PATH
            make_or_check_dir(path=OAUTH2_CONFIG_PATH)
        cls._FILE_PATH = filename
        config.read([filename, ])
        config.set_default_values()
        return config

    def set_default_values(self, force: bool = False):
        """
        Set defaults values for the main OAuth2.0 section
        """
        if force is True or not super(Config, self).has_section(
                self.OAUTH2_SECTION
        ):
            self[self.OAUTH2_SECTION] = dict(
                hostname=OAUTH2_HOSTNAME,
                port=OAUTH2_PORT,
                api_endpoint=OAUTH2_API_ENDPOINT,
                auth_endpoint=OAUTH2_AUTH_ENDPOINT,
                token_endpoint=OAUTH2_TOKEN_ENDPOINT,
                verify_tls=OAUTH2_VERIFY_TLS,
                token_cache_path=OAUTH2_TOKEN_CACHE_PATH,
            )

    def save(self, filename: Optional[str] = None):
        """
        Save configuration to the file
        """
        filename = os.path.expanduser(filename or self._FILE_PATH)
        with open(filename, 'w') as file_descriptor:
            self.write(file_descriptor)

    def has_section(self, section: str) -> bool:
        """
        Check if section exist in configuration
        """
        if section == self.OAUTH2_SECTION:
            return False
        return super(Config, self).has_section(section)
