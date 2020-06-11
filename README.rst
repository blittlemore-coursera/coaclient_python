Coursera OAuth2 client
======================

This project is a library consisting of a command-line interface and a client for interacting with Coursera's OAuth2 authorizes APIs.
It's a rewritten `courseraoauth2client <https://github.com/coursera/courseraoauth2client>`_ with python3 support.

Installation
------------
Create virtualenv using python3::

    virtualenv -p $(which python3) <path_to_env>

Activate created virtualenv::

    source <path_to_env>/bin/activate


To install this SDK, execute::

    pip install coaclient

`pip <https://pip.pypa.io/en/latest/index.html>`_ is a python package manager.

Setup
-----
Before using Coursera's OAuth2 APIs, be sure you know your client id,
client secret, and scopes you want for your application. You may create
an application at https://accounts.coursera.org/console. When creating the
application, set the
``Redirect URI`` to be ``http://localhost:9876/callback``.

Command Line Interface
----------------------

The project includes a command-line tool. Run::

    coaclient -h

for a complete list of features, flags, and documentation.


config
^^^^^^

Configures the Coursera OAuth2 client library.

Examples:
::

    coaclient config add --app APP_NAME

Adds configuration for a new application to coaclient. And also prepares new
storage for application authorization tokens in coaclient.
::

    coaclient config authorize --app APP_NAME

Configures the tool to go through the `authorization secret <https://tools.ietf.org/html/rfc6749#section-4.1>`_ flow for application ``APP``.

The Coaclient tries to open the default system browser(If this step fails, the Coaclient suggests to open a link in the browser manually).
The application configuration will be saved to the local file if the request is succeeded.
You should check the data you've provided to the library during application configuration if you see any errors in the browser.
::

    coaclient config check-auth --app APP_NAME

Checks whether the current instance can authorize against Coursera's API server for application ``APP``
::

    coaclient config display-auth-cache --app APP_NAME

Shows authorization cache for app. The auth and refresh tokens are truncated for security purposes.
If you want to display them, you can add ``--no-truncate option``. Don't pass your tokens to the third parties!

::

    coaclient config delete --app APP_NAME

Delete the application from configuration file if the application exists.

version
^^^^^^^

Returns the current version of the library

Examples:
::

    coaclient version

loglevel
^^^^^^^^
You can suppress output or get more detailed information by choosing a log level.
It can be done by specifying the optional ``--log-level(-l)`` parameter.
Valid choices are ``INFO``, ``DEBUG``, ``WARNING``, ``ERROR``, ``CRITICAL``.
Default loglevel is ``INFO``.

Usage
-----------

::

  import requests
  from coaclient import oauth2
  ...
  app = 'my_application_name'
  url = 'https://api.coursera.org/api/externalBasicProfiles.v1?q=me&fields=name'
  auth = oauth2.build(app=app).authorizer
  response = requests.get(url, auth=auth)
  print response.json()

If ``my_application_name`` was successfully configured, you will be able to
successfully make a request. Otherwise, an exception will be thrown telling you
to set up your application for API access.

Bugs / Issues / Feature Requests
--------------------------------

Please use the Github issue tracker to document any bugs or other issues you
encounter while using this tool.


Tests
^^^^^

To run tests, run: ``nosetests``, or ``tox``.
