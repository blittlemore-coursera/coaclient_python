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
import logging
import os
import pickle
import subprocess
import sys
import time
import uuid
import webbrowser
from argparse import Namespace
from configparser import ConfigParser
from datetime import datetime
from http.server import HTTPServer
from typing import (
    Optional,
    Union,
    List,
    Dict,
    Any,
    Type
)

import requests
from requests.auth import AuthBase

from .config import Config
from .exceptions import (
    OAuth2ConfigError,
    OAuth2ClientException,
    OAuth2TokenExpiredError
)
from .settings import (
    OAUTH2_AUTH_ENDPOINT,
    OAUTH2_TOKEN_ENDPOINT,
    OAUTH2_VERIFY_TLS,
    OAUTH2_TOKEN_CACHE_PATH,
    OAUTH2_HOSTNAME,
    OAUTH2_PORT
)
from .utils import (
    make_or_check_dir,
    CallbackCodeHolder,
    CourseraOAuth2CallbackHandler,
    validate_input_data
)

logger = logging.getLogger()

__all__ = (
    "build",
)


def build(
        app_name: str,
        *,
        args: Optional[Namespace] = None,
        config: Optional[ConfigParser] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        scopes: Optional[Union[List[str], str]] = None,
        token_cache_file: Optional[str] = None,
        **kwargs
):
    """
    Creates a Coursera OAuth client based on the saved or provided
    configuration.
    """

    if app_name is None or not app_name:
        raise OAuth2ConfigError(
            "Please use the correct app name to create OAuth2.0 access to "
            "Coursera API."
        )

    if config is None:
        config_file = args.config if (
            args is not None and args.config is not None
        ) else None
        config = Config.load_from_file(filename=config_file)
        if not config.has_section(app_name):
            raise OAuth2ConfigError(
                "Please configure your App \"{app_name}\" using the "
                "`coaclient` cli tool or provide configuration via config "
                "file prior to use.".format(app_name=app_name)
            )

    return CourseraOAuth2(
        app_name,
        config=config,
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes,
        token_cache_file=token_cache_file,
        **kwargs
    )


class CourseraOAuth2Client(AuthBase):
    """ OAuth2.0 client for authorization in requests to Coursera API """

    def __init__(self, token: str, expires: float) -> None:
        self._token = token
        self._expires = expires

    def __call__(self, request):
        if self.is_valid:
            logging.debug("Adding an authorization header to the request.")
            request.headers["Authorization"] = "Bearer {token}".format(
                token=self._token
            )
            return request
        raise OAuth2TokenExpiredError("Expired at {expires}".format(
            expires=datetime.fromtimestamp(self._expires).strftime(
                "%d-%m-%Y %H:%M:%S"
            )
        ))

    @property
    def is_valid(self) -> bool:
        """
        OAuth2.0 client property.
        is_valid - return True if the token is not expired else False
        """
        return time.time() < self._expires


class CourseraOAuth2:
    """
    This class manages the OAuth2.0 tokens used to access Coursera's APIs.

    You must register your app with Coursera at:

        https://accounts.coursera.org/console

    Construct an instance of this class with the client_id and client_secret
    displayed in the Coursera app console. Please also set a redirect URL to be

        http://localhost:9876/callback

    Note: you can replace the port number (9876 above) with whatever port
    you'd like. If you would not like to use the local webserver to retrieve
    the codes set the local_port field in the constructor to None.
    """
    _TOKEN_TYPE = "BEARER"
    _MAC_OS = "darwin"
    _LINUX = "linux"

    def __init__(
            self,
            app_name: str,
            *,
            config: Optional[Config] = None,
            client_id: Optional[str] = None,
            client_secret: Optional[str] = None,
            scopes: Optional[Union[List[str], str]] = None,
            token_cache_file: Optional[str] = None,
            verify_tls: Optional[bool] = None,
            is_server_callback: bool = True,
            client_class: Type = CourseraOAuth2Client
    ) -> None:
        self.app_name = app_name
        self._config = config or Config.load_from_file()

        self._client_id = client_id or self._config.get(
            self.app_name, "client_id"
        )
        self._client_secret = client_secret or self._config.get(
            self.app_name, "client_secret"
        )
        self._scopes = scopes or self._config.get(self.app_name, "scopes")

        if isinstance(self._scopes, list):
            self._scopes = " ".join(self._scopes)

        self._auth_endpoint = self._config.get(
            self._config.OAUTH2_SECTION,
            "auth_endpoint",
            fallback=OAUTH2_AUTH_ENDPOINT
        )
        self._token_endpoint = self._config.get(
            self._config.OAUTH2_SECTION,
            "token_endpoint",
            fallback=OAUTH2_TOKEN_ENDPOINT
        )
        if verify_tls is not None and verify_tls in [False, True]:
            self._verify_tls = verify_tls
        else:
            self._verify_tls = self._config.getboolean(
                self._config.OAUTH2_SECTION,
                "verify_tls",
                fallback=OAUTH2_VERIFY_TLS
            )
        self._token_cache_path = self._config.get(
            self._config.OAUTH2_SECTION, "token_cache_path",
            fallback=OAUTH2_TOKEN_CACHE_PATH
        )
        self._token_cache_file = os.path.join(
            self._token_cache_path,
            token_cache_file or self._config.get(
                self.app_name, "token_cache_file"
            )
        )
        self._hostname = self._config.get(
            self._config.OAUTH2_SECTION, "hostname", fallback=OAUTH2_HOSTNAME
        )
        self._port = self._config.getint(
            self._config.OAUTH2_SECTION, "port", fallback=OAUTH2_PORT
        )

        self._is_server_callback = is_server_callback
        self._client_class = client_class
        # Cache token variable
        self._cache = None
        make_or_check_dir(path=self._token_cache_path)

    @property
    def cache(self) -> Dict[str, Any]:
        """
        Retrieve token from the file if the cache is empty and return it
        """
        if self._cache is None:
            self._cache = self._load_cache()
        return self._cache

    def _load_cache(self) -> Optional[Dict[str, Any]]:
        """ Reads the local file cache to get pre-authorized access tokens """
        try:
            logging.debug('Reading from local file cache: %s',
                          self._token_cache_file)
            with open(self._token_cache_file, 'rb') as file_descriptor:
                cache = pickle.load(file_descriptor)
                if self._cache_is_valid(cache):
                    logging.debug('Loaded from file system: %s', cache)
                else:
                    logging.warning('Unexpected value found in cache: %s', cache)
            return cache
        except IOError:
            logging.debug("The cache file doesn't exist in the file system: "
                          "%s", self._token_cache_file)
        except Exception as err:
            logging.exception('Unknown cache load exception detected: %s',
                              str(err), exc_info=True)

    @cache.setter
    def cache(self, cache: Dict[str, Any]):
        self._cache = cache
        self._save_cache(cache)

    def _save_cache(self, cache: Dict[str, Any]) -> None:
        """ Writes out OAuth2.0 tokens to the file a cache. """
        logging.debug('Writing to the local cache OAuth2.0 tokens.')
        if not self._cache_is_valid(cache):
            logging.error('Attempt to save invalid OAuth2 tokens: %s', cache)
            return

        try:
            logging.debug('Writing to cache file: %s', self._token_cache_file)
            with open(self._token_cache_file, 'wb') as file_descriptor:
                pickle.dump(cache, file_descriptor, protocol=-1)
                logging.debug('OAuth2.0 tokens successfully saved to '
                              'the cache file.')
        except Exception as err:
            logging.exception("Couldn't successfully cache OAuth2 tokens to "
                              "the cache file: %s", str(err), exc_info=True)

    @staticmethod
    def _cache_is_valid(cache: Dict[str, Any]) -> bool:
        """ Checks the cache for appropriate type correctness. """
        return (isinstance(cache, dict) and
                isinstance(cache.get("token"), str) and
                isinstance(cache.get("expires"), float) and
                (isinstance(cache.get("refresh"), str) or True))

    @property
    def _redirect_uri(self):
        return 'http://{hostname}:{port}/callback'.format(
            hostname=self._hostname,
            port=self._port,
        )

    def _build_auth_url(self, state: str) -> Optional[str]:
        auth = requests.Request(
            method='GET',
            url=self._auth_endpoint,
            params={
                'access_type': 'offline',
                'response_type': 'code',
                'client_id': self._client_id,
                'redirect_uri': self._redirect_uri,
                'scope': self._scopes,
                'state': state,
            }
        ).prepare()
        logging.debug('Constructed authorization request url: %s', auth.url)
        return auth.url

    def _auth_new_app(self):
        """
        Stands up a new localhost HTTP server and retrieves new OAuth2.0
        access tokens from the Coursera OAuth2.0 service.
        """
        logging.info('Requesting the new OAuth2.0 tokens from Coursera.')

        # Attempt to request new tokens from Coursera via the browser.
        state = uuid.uuid4().hex
        auth_url = self._build_auth_url(state)

        logging.info('Please visit the following URL to authorize this app.')
        logging.info(auth_url)
        logging.info('Look for additional details in the browser.')
        if sys.platform == self._MAC_OS:
            # OS X -- leverage the 'open' command present on all modern macs
            logging.info('Mac OS X detected; attempting to auto-open '
                         'the url in your default browser...')
            try:
                subprocess.check_call(['open', auth_url])
            except Exception as err:
                logging.exception('Could not call `open %s`. Exception: %s',
                                  auth_url, str(err))
        elif sys.platform == self._LINUX:
            logging.info('Linux detected; attempting to auto-open '
                         'the url in your default browser...')
            try:
                webbrowser.open(auth_url)
            except (TypeError, Exception) as err:
                logging.exception('Could not call `open %s`. Exception: %s',
                                  auth_url, str(err))

        if self._port is not None:
            # Boot up a local webserver to retrieve the response.
            code = CallbackCodeHolder()
            handler = CourseraOAuth2CallbackHandler
            handler.CALLBACK = code
            handler.STATE = state

            server = HTTPServer((self._hostname, self._port), handler)

            while not code.exist:
                server.handle_request()
            code = code.code
        else:
            code = validate_input_data(
                "Please enter the code received from Coursera: ", empty=False
            )

        return self._get_tokens_from_coursera({
            'code': code,
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'redirect_uri': self._redirect_uri,
            'grant_type': 'authorization_code',
        })

    def _get_tokens_from_coursera(
            self, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send the request to the Coursera token endpoint
        to get the new access token.
        """
        logging.debug('Send data %s to token endpoint %s',
                      data, self._token_endpoint)

        response = requests.post(
            url=self._token_endpoint, data=data,
            verify=self._verify_tls, timeout=10,
        )

        logging.debug('Response from token endpoint: (%s) %s',
                      response.status_code, response.text)

        if response.status_code != requests.codes.ok:  # pylint: disable=no-member
            logging.error(
                'Encountered unexpected status code. Status code: %s '
                'Response text: %s Response %s',
                response.status_code, response.text, response
            )
            raise OAuth2ClientException(
                'Unexpected status code from token endpoint. '
                'Status code: {status_code} '
                'Response text: {response_text}'.format(
                    status_code=response.status_code,
                    response_text=response.text
                )
            )
        # Parse JSON response data
        response_data = response.json()
        try:
            # Checking type of received token
            if response_data['token_type'].upper() != self._TOKEN_TYPE:
                logging.error('Unknown token type encountered in response '
                              'data: %s', response_data['token_type'])
                raise OAuth2ClientException(
                    'Unknown token type encountered in response data: '
                    '{token_type}'.format(
                        token_type=response_data['token_type']
                    )
                )
            tokens = {
                'token': response_data['access_token'],
                'expires': time.time() + response_data['expires_in']
            }
            refresh_token = response_data.get('refresh_token')
            if refresh_token is not None and isinstance(refresh_token, str):
                tokens['refresh'] = refresh_token
            return tokens
        except (KeyError, TypeError, AttributeError):
            logging.error('Some fields malformed or missing in the '
                          'response data. %s', response_data)
            raise OAuth2ClientException(
                'Some fields malformed or missing in the response data. '
                '{response_data}'.format(response_data=response_data)
            )

    def _exchange_refresh_tokens(self) -> Optional[Dict[str, Any]]:
        """
        Exchanges a refresh token for an access token
        """
        refresh_token = (self.cache or {}).get('refresh')
        tokens = None
        if refresh_token is not None:
            # Attempt to use the refresh token to get a new access token.
            tokens = self._get_tokens_from_coursera({
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': self._client_id,
                'client_secret': self._client_secret,
            })
            tokens['refresh'] = refresh_token
        return tokens

    def _is_token_expired(self) -> bool:
        """
        The cache shouldn't be null and expired.
        """
        return self.cache is None or self.cache.get('expires', 0) < time.time()

    def refresh(self) -> bool:
        """
        Refresh tokens for access to Coursera API.
        """
        _tokens = self._exchange_refresh_tokens()
        if _tokens is not None:
            self.cache = _tokens
            return True
        return False

    @property
    def authorizer(self):
        """
        Checks cache, updates tokens if required and returns CourseraOAuth2Auth
        """
        if self._is_token_expired():
            logging.debug(
                "Attempting to use a refresh token to get new token."
            )
            _tokens = self._exchange_refresh_tokens()
            if _tokens is None:
                logging.info("Attempting to retrieve new tokens from the "
                             "auth endpoint. You will be prompted to "
                             "authorize your app in your web browser.")
                _tokens = self._auth_new_app()
                logging.debug("New received tokens: %s", _tokens)
            self.cache = _tokens
        else:
            logging.debug("Local cache with your tokens is good.")

        return self._client_class(self.cache.get('token'),
                                  self.cache.get('expires'))
