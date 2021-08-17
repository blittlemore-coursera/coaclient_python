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
CoaClient OAuth2.0 exceptions
"""
from coaclient.exceptions.base import CoaClientBaseException

__all__ = (
    "OAuth2ClientException",
    "OAuth2ConfigError",
    "OAuth2CacheException",
    "OAuth2TokenExpiredError",
)


class OAuth2ClientException(CoaClientBaseException):
    """ OAuth2.0 client exception class for custom exception """
    _STR = "Coursera OAuth2.0 client exception by OAuth2.0 protocol: {message}"


class OAuth2ConfigError(CoaClientBaseException):
    """ Coursera OAuth2.0 Config custom error class """
    _STR = "Coursera OAuth2.0 configuration error: {message}"


class OAuth2CacheException(CoaClientBaseException):
    """ Coursera OAuth2.0 Cache custom exception class """


class OAuth2TokenExpiredError(CoaClientBaseException):
    """ OAuth2.0 token expired error class """
    _STR = "Coursera OAuth2.0 token expired error: {message}"
