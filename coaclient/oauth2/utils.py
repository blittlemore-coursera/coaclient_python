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
import errno
import logging
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import status

from .exceptions import OAuth2CacheException, OAuth2ConfigError

__all__ = (
    "validate_input_data",
    "make_or_check_dir",
    "CourseraOAuth2CallbackHandler",
    "CallbackCodeHolder",
)


def validate_input_data(
        message: str,
        empty: bool = True,
        num_of_repeat: int = 3
):
    """
    Validation of input user data from CLI
    """
    if empty is True:
        return input(message).strip()

    counter = 0
    while True:
        value = input(message).strip()
        if not value:
            counter += 1
            logging.warning("Input value can't be empty. Please try again.")
        else:
            break
        if counter == num_of_repeat:
            raise OAuth2ConfigError(
                "Something wrong with your input data. Please look at input "
                "data and try again later."
            )
    return value


def make_or_check_dir(path: str):
    """
    Checking directory exist or no:
    1. if not exist creating it
    2. If exist check dir permissions
    """
    if not os.path.exists(path):
        try:
            os.makedirs(path, mode=0o700)
        except OSError as err:
            logging.debug(
                'Encountered an exception creating a directory for token '
                'cache file. Ignore it ...', exc_info=True
            )
            if err.errno != errno.EEXIST:
                raise
    else:
        permissions = oct(os.stat(path).st_mode)[-3:]
        if permissions != '700':
            raise OAuth2CacheException(
                "You have wrong permissions for token cache directory: "
                "{path}".format(path=path)
            )


class CallbackCodeHolder:
    """ A helper class to hold a token. """

    def __init__(self) -> None:
        self.code = None

    def __call__(self, code: str) -> None:
        self.code = code

    @property
    def exist(self) -> bool:
        """ Check if the code already stored in holder. """
        return self.code is not None


# Local Server handler to receive code from Coursera after authorization.
# That code used to get access tokens from Coursera to use Coursera API.
class CourseraOAuth2CallbackHandler(BaseHTTPRequestHandler):
    """ HTTPRequest handler class """
    _CALLBACK_PATH = "/callback"
    STATE = None
    CALLBACK = (lambda code: code)

    def _make_response(self, code: int, content: bytes):
        self.send_response(code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(content)

    def _make_error_response(self, message):
        """ Return response with the error that raised """
        logging.warning('Return response with the error that raised:'
                        ' %s. %s', message, self.path)
        self._make_response(
            code=status.HTTP_400_BAD_REQUEST,
            content=message.encode("utf-8")
        )

    def do_GET(self):  # pylint: disable=invalid-name
        """ GET request processing """
        parsed = urlparse(self.path)

        if not parsed.query or parsed.path != self._CALLBACK_PATH:
            return self._make_error_response(
                "We encountered problems with your request."
            )

        params = parse_qs(parsed.query)
        # Checking state generated and received tokens
        if params.get('state') != [self.STATE, ]:
            return self._make_error_response(
                "State tokens didn't match. Please use last generated "
                "authorization URL to get access tokens."
            )

        code = params.get('code', [])
        if len(code) != 1:
            return self._make_error_response(
                "The wrong count of \"code\" values in query parameters."
            )

        if self.CALLBACK and callable(self.CALLBACK):
            self.CALLBACK(params['code'][0])

        return self._make_response(
            code=status.HTTP_200_OK,
            content="We have captured Coursera's response code. Feel "
                    "free to close this browser and come back to your "
                    "terminal. Thanks!".encode("utf-8")
        )
