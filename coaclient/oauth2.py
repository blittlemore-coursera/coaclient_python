#!/usr/bin/env python

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
Helpers for working with OAuth2 / etc.
"""

import _pickle
import configparser
import errno
import logging
import os
import os.path
import re
import subprocess
import sys
import time
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import requests
import status
from requests.auth import AuthBase

from coaclient.utils import validate_not_empty_input

CONFIG_DIR = os.path.join(os.getenv('HOME', ''), '.coursera')
CONFIG_FILE_NAME = 'coaclient.cfg'


class ExpiredToken(Exception):
    """
    Expired token custom exception class
    """
    def __init__(self, oauth2_auth):
        self.oauth2_auth = oauth2_auth

    def __str__(self):
        return 'Attempt to use expired token. Expired at: %s.' % (
            self.oauth2_auth.expires)


class OAuth2Exception(Exception):
    """
    OAuth2Exception custom exception class
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return 'OAuth2 Protocol Exception: %(msg)s' % {'msg': self.msg}


class OAuth2ConfigurationException(Exception):
    """
    Oauth2Configuration custom exception class
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return 'OAuth2 Configuration Exception. %(msg)s' % {'msg': self.msg}


class CourseraOAuth2Auth(AuthBase):
    """Attaches OAuth2 access tokens to requests."""

    def __init__(self, token, expires):
        self.token = token
        self.expires = expires

    def is_valid(self):
        """Determines if this authorizer is still valid."""
        return time.time() < self.expires

    def __call__(self, request):
        if self.is_valid():
            logging.debug('About to add an authorization header!')
            request.headers['Authorization'] = 'Bearer %(token)s' % {
                'token': self.token
            }
            return request

        logging.error(
            'Attempt to use expired Authorizer. Expired: %s, now: %s',
            self.expires, time.time()
        )
        raise ExpiredToken(self)


class CodeHolder:
    """A helper class to hold a token."""

    def __init__(self):
        self.code = None

    def __call__(self, code):
        self.code = code

    def has_code(self):
        """Check if the code already stored in holder"""
        return self.code is not None


def _make_handler(state_token, done_function):
    """
    Makes a a handler class to use inside the basic python HTTP server.

    state_token is the expected state token.
    done_function is a function that is called, with the code passed to it.
    """
    class LocalServerHandler(BaseHTTPRequestHandler):
        """
        HTTP request handler class
        """

        def error_response(self, msg):
            """
            Handle error response
            """
            logging.warning(
                'Error response: %(msg)s. %(path)s', msg, path=self.path
            )
            self.send_response(status.HTTP_400_BAD_REQUEST)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(msg)

        def do_GET(self):
            """Serve a GET request."""
            parsed = urlparse(self.path)
            if not parsed.query or parsed.path != '/callback':
                self.error_response(
                    'We encountered a problem with your request.')
                return

            params = parse_qs(parsed.query)
            if params.get('state') != [state_token]:
                self.error_response(
                    'Attack detected: state tokens did not match!'
                )
                return

            if len(params.get('code', [])) != 1:
                self.error_response('Wrong number of "code" query parameters.')
                return

            self.send_response(status.HTTP_200_OK)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(
                b"coaclient: we have captured Coursera's response "
                b"code. Feel free to close this browser window now and return "
                b"to your terminal. Thanks!"
            )
            done_function(params['code'][0])

    return LocalServerHandler


OAUTH2_URL_BASE = 'https://accounts.coursera.org/oauth2/v1/'


def check_and_create_directory(dir_name):
    """Checking if directory exists and creating it"""
    if not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name, mode=0o700)
        except OSError as exc:
            logging.debug(
                'Encountered an exception creating directory for token '
                'cache file. Ignoring...',
                exc_info=True
            )
            if exc.errno != errno.EEXIST:
                raise


class CourseraOAuth2:
    """
    This class manages the OAuth2 tokens used to access Coursera's APIs
    You must register your app with Coursera at:

        https://accounts.coursera.org/console

    Construct an instance of this class with the client_id and client_secret
    displayed in the Coursera app console. Please also set a redirect url to be

        http://localhost:9876/callback

    Note: you can replace the port number (9876 above) with whatever port you'd
    like. If you would not like to use the local webserver to retrieve the
    codes set the local_port field in the constructor to None.

    TODO: add usage / more documentation.
    """

    def __init__(
            self,
            client_id,
            client_secret,
            scopes,
            token_cache_file,
            verify_tls=True,
            local_port=9876
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes
        self.auth_endpoint = OAUTH2_URL_BASE + 'auth'
        self.token_endpoint = OAUTH2_URL_BASE + 'token'
        self.verify_tls = verify_tls
        self.token_cache_file = os.path.expanduser(token_cache_file)
        # Create the appropriate directory if it doesn't exist
        dir_name = os.path.dirname(self.token_cache_file)
        if not os.path.isfile(self.token_cache_file):
            check_and_create_directory(dir_name)
        else:
            dir_permissions = oct(os.stat(dir_name).st_mode)[-3:]
            if dir_permissions != '700':
                raise Exception(
                    "You have wrong permissions for {}".format(dir_name)
                )

        # If not None run a local webserver to listen to the callback url
        self.local_port = local_port
        self._token_cache = None

    @property
    def _redirect_uri(self):
        return 'http://%(hostname)s:%(port)s/callback' % {
            'hostname': 'localhost',
            'port': self.local_port,
        }

    @property
    def token_cache(self):
        """Retrieve token from file if not exists in cache and return it"""
        if self._token_cache is None:
            # Load token cache from the file system.
            self._token_cache = self._load_token_cache()
        return self._token_cache

    @token_cache.setter
    def token_cache(self, value):
        self._token_cache = value
        self._save_token_cache(value)

    def _load_token_cache(self):
        """Reads the local fs cache for pre-authorized access tokens"""
        try:
            logging.debug(
                'Reading from local file cache file %s', self.token_cache_file
            )
            with open(self.token_cache_file, 'rb') as _file:
                fs_cached = _pickle.load(_file)
                if self._check_token_cache_type(fs_cached):
                    logging.debug('Loaded from file system: %s', fs_cached)
                    return fs_cached
                logging.warning(
                    'Found unexpected value in cache. %s', fs_cached
                )
                return None
        except IOError:
            logging.debug(
                'Did not find the file: %s on the file system.',
                self.token_cache_file
            )
            return None
        except:
            logging.info(
                'Encountered an exception loading from the file system.',
                exc_info=True)
            return None

    def _save_token_cache(self, new_cache):
        """Write out to the filesystem a cache of the OAuth2 information."""
        logging.debug('Writing to local authentication cache...')
        if not self._check_token_cache_type(new_cache):
            logging.error('Attempt to save a bad value: %s', new_cache)
            return
        try:
            logging.debug(
                'Writing to fs cache file: %s', self.token_cache_file
            )
            with open(self.token_cache_file, 'wb') as _file:
                _pickle.dump(new_cache, _file, protocol=-1)
                logging.debug('Finished dumping cache_value to fs cache file.')
        except:
            logging.exception(
                "Couldn't successfully cache OAuth2 secrets on the file system"
            )

    @staticmethod
    def _check_token_cache_type(cache_value):
        """
        Checks the cache_value for appropriate type correctness.

        Pass strict=True for strict validation to ensure the latest types are
        being written.

        Returns True if type is correct, False otherwise.
        """

        def check_string_value(name):
            return isinstance(cache_value[name], str)

        def check_refresh_token():
            if 'refresh' in cache_value:
                return check_string_value('refresh')

            return True

        return (
            isinstance(cache_value, dict) and
            'token' in cache_value and
            'expires' in cache_value and
            check_string_value('token') and
            isinstance(cache_value['expires'], float) and
            check_refresh_token()
        )

    def _request_tokens_from_token_endpoint(self, form_data):
        logging.debug(
            'Posting form data %s to token endpoint %s',
            form_data,
            self.token_endpoint
        )
        response = requests.post(
            self.token_endpoint,
            data=form_data,
            verify=self.verify_tls,
            timeout=10,
        )

        logging.debug(
            'Response from token endpoint: (%s) %s',
            response.status_code,
            response.text
        )

        if response.status_code != status.HTTP_200_OK:
            logging.error(
                'Encountered unexpected status code: %s %s %s',
                response.status_code,
                response,
                response.text
            )
            raise OAuth2Exception('Unexpected status code from token endpoint')

        body = response.json()
        try:
            access_token = body['access_token']
            expires_time = time.time() + body['expires_in']
            token_type = body['token_type'].lower()
            refresh = body.get('refresh_token')
        except (KeyError, TypeError, AttributeError):
            logging.error(
                'Malformed / missing fields in body. %(body)s', body=body
            )
            raise OAuth2Exception(
                'Malformed response body from token endpoint.'
            )

        if token_type != 'bearer':
            logging.error(
                'Unknown token_type encountered: %s', body['token_type']
            )
            raise OAuth2Exception('Unknown token_type encountered.')

        tokens = {
            'token': access_token,
            'expires': expires_time,
        }

        if isinstance(refresh, str):
            tokens['refresh'] = refresh

        return tokens

    def _build_authorizaton_url(self, state_token):
        authorization_request = requests.Request(
            'GET',
            self.auth_endpoint,
            params={
                'access_type': 'offline',
                'response_type': 'code',
                'client_id': self.client_id,
                'redirect_uri': self._redirect_uri,
                'scope': self.scopes,
                'state': state_token,
            }
        ).prepare()

        logging.debug(
            'Constructed authoriation request at: %s',
            authorization_request.url
        )
        return authorization_request.url

    def _authorize_new_tokens(self):
        """
        Stands up a new localhost http server and retrieves new OAuth2 access
        tokens from the Coursera OAuth2 server.
        """
        logging.info('About to request new OAuth2 tokens from Coursera.')
        # Attempt to request new tokens from Coursera via the browser.
        state_token = uuid.uuid4().hex
        authorization_url = self._build_authorizaton_url(state_token)

        sys.stdout.write(
            'Please visit the following URL to authorize this app:\n'
        )
        sys.stdout.write('\t%s\n\n' % authorization_url)
        sys.stdout.write('Look for additional details in the browser:\n')
        if sys.platform == 'darwin':
            # OS X -- leverage the 'open' command present on all modern macs
            sys.stdout.write(
                'Mac OS X detected; attempting to auto-open '
                'the url in your default browser...\n'
            )
            try:
                subprocess.check_call(['open', authorization_url])
            except:
                logging.exception(
                    'Could not call `open %(url)s`.', url=authorization_url
                )

        elif sys.platform == 'linux':
            sys.stdout.write(
                'Linux detected; attempting to auto-open '
                'the url in your default browser...\n'
            )
            try:
                webbrowser.open(authorization_url)
            except TypeError:
                logging.exception(
                    'Could not call `open %(url)s`.', url=authorization_url
                )

        if self.local_port is not None:
            # Boot up a local webserver to retrieve the response.
            server_address = ('', self.local_port)
            code_holder = CodeHolder()

            local_server = HTTPServer(
                server_address, _make_handler(state_token, code_holder)
            )

            while not code_holder.has_code():
                local_server.handle_request()
            coursera_code = code_holder.code
        else:
            coursera_code = input('Please enter the code from Coursera: ')

        form_data = {
            'code': coursera_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self._redirect_uri,
            'grant_type': 'authorization_code',
        }
        return self._request_tokens_from_token_endpoint(form_data)

    def _exchange_refresh_tokens(self):
        """Exchanges a refresh token for an access token"""
        if self.token_cache is not None and 'refresh' in self.token_cache:
            # Attempt to use the refresh token to get a new access token.
            refresh_form = {
                'grant_type': 'refresh_token',
                'refresh_token': self.token_cache['refresh'],
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            }
            try:
                tokens = self._request_tokens_from_token_endpoint(refresh_form)
                tokens['refresh'] = self.token_cache['refresh']
                return tokens
            except OAuth2Exception:
                logging.exception(
                    'Encountered an exception during refresh token flow.'
                )
        return None

    def _cache_has_good_token(self):
        """The cache must have a token, and it must expire in > 5 minutes"""
        return (
            self.token_cache is not None and
            (time.time() + 5 * 60) < self.token_cache['expires']
        )

    def build_authorizer(self):
        """
        Checks cache, updates tokens if required and returns CourseraOAuth2Auth
        """
        if not self._cache_has_good_token():
            logging.debug('Attempting to use a refresh token.')
            new_tokens = self._exchange_refresh_tokens()
            if new_tokens is None:
                logging.info(
                    'Attempting to retrieve new tokens from the endpoint. '
                    'You will be prompted to authorize your app '
                    'in your web browser.'
                )
                new_tokens = self._authorize_new_tokens()
            logging.debug('New tokens: %s', new_tokens)
            self.token_cache = new_tokens
        else:
            logging.debug('Local cache is good.')
        return CourseraOAuth2Auth(
            self.token_cache['token'], self.token_cache['expires']
        )


def build_oauth2(app, args=None, cfg=None):
    """
    Creates CourseraOAuth based on configuration
    """
    if not app:
        raise OAuth2ConfigurationException(
            "Please enter an app name for OAuth2 access"
        )

    if cfg is None:
        cfg = configuration()
        if not cfg.has_section(app) and not args:
            raise OAuth2ConfigurationException(
                'Please configure app "%s" using the `coaclient` '
                'command line tool prior to use' % app
            )
        if not cfg.has_section(app) or (args and args.reconfigure):
            configure_app(app, cfg)

    try:
        client_id = args.client_id
    except AttributeError:
        client_id = cfg.get(app, 'client_id')

    try:
        client_secret = args.client_secret
    except AttributeError:
        client_secret = cfg.get(app, 'client_secret')

    try:
        scopes = args.scopes
    except AttributeError:
        scopes = cfg.get(app, 'scopes')

    try:
        cache_filename = args.token_cache_file
    except AttributeError:
        dirname = cfg.get('oauth2', 'token_cache_base')
        sanitized_app = re.sub(r'[^\w\-\_.]', '_', app)
        filename = '%s_oauth2_cache.pickle' % sanitized_app
        cache_filename = os.path.join(dirname, filename)

    return CourseraOAuth2(
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes,
        token_cache_file=cache_filename
    )


def delete_application(app):
    """Delete application from config file"""
    cfg = configuration()
    available_apps = [app for app in cfg.sections() if app != 'oauth2']
    if app not in available_apps:
        raise Exception('Application {} not found'.format(app))

    while True:
        choice = input(
            'Are you sure you want to delete application {}?(y/N) '.format(
                app)).strip().lower()
        if choice in ('yes', 'y'):
            print('Deleting app {}'.format(app))
            cfg.remove_section(app)
            write_config_to_file(cfg)
            logging.info('Application "%s" was removed', app)
            break

        if choice in ('no', 'n'):
            break


def write_config_to_file(cfg):
    """Save configuration to config file"""
    cfg_path = os.path.expanduser(os.path.join(CONFIG_DIR, CONFIG_FILE_NAME))
    with open(cfg_path, 'w') as configfile:
        cfg.write(configfile)


def configure_app(app_name, cfg):
    """Creates application configuration for an organization"""
    logging.info('Configuring application "%s"', app_name)
    cfg.remove_section(app_name)
    cfg.add_section(app_name)
    client_id = validate_not_empty_input('Please enter the client id: ')
    client_secret = validate_not_empty_input(
        'Please enter the client secret: '
    )
    scopes = input(
        'Please enter the requested scopes of the app not '
        'including "view_profile", separated by whitespace:\n'
        'E.g: access_business_api'
    )
    cfg.set(app_name, 'client_id', client_id)
    cfg.set(app_name, 'client_secret', client_secret)
    cfg.set(app_name, 'scopes', "view_profile %s" % scopes)
    check_and_create_directory(CONFIG_DIR)
    write_config_to_file(cfg)
    logging.info('Application "%s" configured!', app_name)


def configuration():
    """Loads configuration from the file system."""
    cfg = configparser.ConfigParser()
    cfg['oauth2'] = {
        'hostname': 'localhost',
        'port': 9876,
        'api_endpoint': 'https://api.coursera.org',
        'auth_endpoint': 'https://accounts.coursera.org/oauth2/v1/auth',
        'token_endpoint': 'https://accounts.coursera.org/oauth2/v1/token',
        'verify_tls': True,
        'token_cache_base': CONFIG_DIR
    }

    cfg.read([os.path.join(CONFIG_DIR, CONFIG_FILE_NAME)])
    return cfg
