# Copyright 2020-2021 Coursera
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
CoaClient exceptions
"""
from coaclient.exceptions.base import CoaClientBaseException
from coaclient.exceptions.commands import CoaClientCommandException
from coaclient.exceptions.oauth2 import (
    OAuth2ClientException,
    OAuth2ConfigError,
    OAuth2CacheException,
    OAuth2TokenExpiredError
)

__all__ = (
    "CoaClientBaseException",
    "OAuth2ClientException",
    "OAuth2ConfigError",
    "OAuth2CacheException",
    "OAuth2TokenExpiredError",
    "CoaClientCommandException",
)
