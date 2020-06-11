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
Coursera OAuth2 client command

Command: config
"""

import logging
import os
import re
import time

import requests

from coaclient import oauth2
from coaclient.cli import Parser, SubParser, Arg, Actions
from coaclient.oauth2 import Config
from coaclient.oauth2.utils import validate_input_data
from .exceptions import CoaClientCommandException

__all__ = (
    "add_command",
)


_REGEXP_FILE_NAME = re.compile(r'[^\w\-\_.]')


def add_app(args):
    """
    Adding configuration and credentials for a specific application for
    authorizing in Coursera OAuth2.0 client.
    """
    app_name = args.app
    config_file = args.config if args.config is not None else None
    config = Config.load_from_file(filename=config_file)
    if not config.has_section(app_name) or args.reconfigure is True:
        logging.info(
            "Configuration application \"%s\" for Coursera OAuth2.0 client.",
            app_name
        )
        # Get client_id
        client_id = args.client_id or validate_input_data(
            "Please enter the client id for your application: ",
            empty=False
        )
        # Get client_secret
        client_secret = args.client_secret or validate_input_data(
            "Please enter the client secret for your application: ",
            empty=False
        )
        # Get scopes
        if args.scopes:
            scopes = args.scopes
        else:
            scopes = validate_input_data(
                "Please enter the requested scopes of the app not including "
                "\"view_profile\", separated by whitespace\n(for example: "
                "access_business_api): "
            )

        # Removing app section if exist
        config.remove_section(app_name)
        # Adding new empty app section
        config.add_section(app_name)
        # Adding application credentials to config
        config.set(app_name, "client_id", client_id)
        config.set(app_name, "client_secret", client_secret)
        config.set(app_name, "scopes", "view_profile {scopes}".format(
            scopes=scopes
        ))
        config.set(
            app_name, "token_cache_file", "{app_name}_oauth2_cache.co".format(
                app_name=re.sub(_REGEXP_FILE_NAME, "_", app_name).lower()
            )
        )

        # Save config to file
        config.save(filename=config_file)
        logging.info("Application \"%s\" configured.", app_name)
    else:
        logging.info(
            "Application \"%s\" is already configure and saved to the config "
            "file. You can reconfigure this application if you remove the "
            "config file or use \"%s\" flag when adding configuration for "
            "your application.", app_name, "--reconfigure"
        )


def authorize(args):
    """
    Authorizes Coursera OAuth2.0 client for a specific application
    for using coursera.org API
    """
    if oauth2.build(args.app, args=args).authorizer:
        logging.info("Application \"%s\" authorized.", args.app)
    else:
        logging.error("Something wrong. Application \"%s\" is not "
                      "authorized.", args.app)


def check_auth(args):
    """
    Checking if Coursera OAuth2.0 client connectivity to the coursera.org API
    for a specific application
    """
    profile_url = ("https://api.coursera.org/api/externalBasicProfiles.v1?"
                   "q=me&fields=name")
    response = requests.get(
        profile_url, auth=oauth2.build(args.app, args=args).authorizer
    )

    if response.status_code != requests.codes.ok:  # pylint: disable=no-member
        logging.error('Received response status code %s from the basic '
                      'profile API.', response.status_code)
        logging.debug('Response body: %s', response.text)
        raise Exception('Received response status code {code} from the basic '
                        'profile API.'.format(code=response.status_code))

    response_data = response.json()

    if "elements" in response_data and len(response_data["elements"]) > 0:
        element = response_data["elements"][0]

        if not isinstance(element, dict):
            raise CoaClientCommandException(
                "An invalid data type was received from Coursera OAuth2.0 "
                "API. Type: {type}, Data: {element}".format(
                    type=type(element), element=element
                )
            )

        external_id = element.get("id")

        if external_id is None:
            raise CoaClientCommandException(
                "Could not find the 'external_id' from the response body. "
                "Data: {element}".format(element=element)
            )

        name = element.get("name")

        if name is None:
            raise CoaClientCommandException(
                "Could not find the 'name' from the response body. Data: "
                "{element}".format(element=element)
            )

        logging.info("Name: %s", name)
        logging.info("External ID: %s", external_id)
    else:
        raise CoaClientCommandException(
            "Incorrect data was received from the Coursera OAuth2.0 API. "
            "Data: {response_data}".format(response_data=response_data)
        )


def display_auth_cache(args):
    """
    Output to the screen the state of the authentication cache.

    DEVELOPER NOTE: For debugging authentication issues.

    BEWARE: DO NOT send them to third-party service or via email!!!
    You must keep the tokens secure.
    Treat them as passwords.
    """
    auth = oauth2.build(args.app, args=args)

    token = auth.cache.get('token', '')
    expires = auth.cache.get('expires', 0.0) - time.time()
    refresh = auth.cache.get('refresh', None)
    if not args.no_truncate:
        token = "{}**********{}".format(token[:3], token[-3:])
        if refresh is not None:
            refresh = "{}**********{}".format(refresh[:3], refresh[-3:])

    logging.info("Authorization token: %s", token)
    logging.info(
        "Authorization token is already expired."
        if expires < 0 else
        "Authorization token expires in %.2f seconds",
        expires
    )
    if refresh is not None:
        logging.info("Refresh token: %s", refresh)
    else:
        logging.warning("Refresh token not found.")


def delete(args):
    """
    Delete the application from the configuration if the application exists.
    """
    # oauth2.delete_application(args.app)
    app_name = args.app
    config_file = args.config if args.config is not None else None
    config = Config.load_from_file(filename=config_file)
    if not config.has_section(app_name):
        raise CoaClientCommandException(
            "Configuration for {app_name} application does not exist or "
            "already removed from configuration file.".format(
                app_name=app_name
            )
        )

    choice = validate_input_data(
        "Are you absolutely sure that you want to delete the application "
        "{app_name}? (Y/N): ".format(app_name=app_name)
    ).strip().lower()

    if choice in ("yes", "y"):
        logging.info("Deleting the application \"%s\"", app_name)
        cache_file = os.path.join(
            config.get(config.OAUTH2_SECTION, "token_cache_path"),
            config.get(app_name, "token_cache_file")
        )
        if os.path.exists(cache_file) and os.path.isfile(cache_file):
            os.remove(cache_file)
        config.remove_section(app_name)
        config.save(config_file)
        logging.info("Application \"%s\" was removed", app_name)


def add_command(cli_factory):
    """
    Create config command with command handlers for configure sub commands and
    add to the Coursera's CLI
    """
    config = Parser(
        name="config",
        help="Configure %(prog)s for OAuth2.0 operations",
        subparser=SubParser()
    )
    cli_factory.parser.subparser.parsers.append(config)
    cli_factory.add_arguments(app=Arg(
        flags=("-a", "--app"),
        type=str,
        required=True,
        help="Name of application to configure"
    ), reconfigure=Arg(
        flags=("--reconfigure",),
        action=Actions.STORE_TRUE,
        help="Reconfigure existing application."
    ), no_truncate=Arg(
        flags=("--no-truncate",),
        action=Actions.STORE_TRUE,
        help="[!!! DANGER !!!] Do not truncate the keys. [!!! DANGER !!!].\n"
             "Do that on your own risk and we think you understand that "
             "you do."
    ), client_id=Arg(
        flags=("--client-id",),
        type=str,
        help="Application client id."
    ), client_secret=Arg(
        flags=("--client-secret",),
        type=str,
        help="Application client secret."
    ), scopes=Arg(
        flags=("--scopes",),
        action=Actions.APPEND,
        type=str,
        help="Application scopes. (E.g: view_profile or access_business_api)"
    ))

    # Create sub commands for config command
    # 1. add
    config.subparser.parsers.append(Parser(
        name="add",
        func=add_app,
        help="Adding configuration and credentials for a specific application "
             "for authorizing in Coursera OAuth2.0 client.",
        args=['app', 'reconfigure', 'client_id', 'client_secret', 'scopes']
    ))
    # 2. authorize
    config.subparser.parsers.append(Parser(
        name="authorize",
        func=authorize,
        help="Authorizes Coursera OAuth2.0 client for a specific application"
             " for using coursera.org API",
        args=['app', ]
    ))
    # 3. check-auth
    config.subparser.parsers.append(Parser(
        name="check-auth",
        func=check_auth,
        help="Check Coursera OAuth2.0 client connectivity to the coursera.org "
             "API for a specific application",
        args=['app', ]
    ))
    # 4. display-auth-cache
    config.subparser.parsers.append(Parser(
        name="display-auth-cache",
        func=display_auth_cache,
        help="Output to the screen the state of the authentication cache.\n"
             "BEWARE: DO NOT send them to third-party service or via "
             "email!!!\nYou must keep the tokens secure.\nTreat them as "
             "passwords.",
        args=['app', 'no_truncate']
    ))
    # 5. delete
    config.subparser.parsers.append(Parser(
        name="delete",
        func=delete,
        help="Delete the application from configuration file if the "
             "application exists",
        args=['app', ]
    ))
