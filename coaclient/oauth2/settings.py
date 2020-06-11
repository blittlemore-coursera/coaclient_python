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
Coursera OAuth default settings
"""
import os as _os

OAUTH2_CONFIG_DIR = ".coursera"
OAUTH2_CONFIG_PATH = _os.path.join(_os.getenv("HOME", ""), OAUTH2_CONFIG_DIR)
OAUTH2_CONFIG_FILE_NAME = "coaclient.cfg"
OAUTH2_HOSTNAME = "localhost"
OAUTH2_PORT = 9876
OAUTH2_API_ENDPOINT = "https://api.coursera.org"
OAUTH2_BASE_ENDPOINT = "https://accounts.coursera.org/oauth2/v1"
OAUTH2_AUTH_ENDPOINT = "{base_endpoint}/auth".format(
    base_endpoint=OAUTH2_BASE_ENDPOINT
)
OAUTH2_TOKEN_ENDPOINT = "{base_endpoint}/token".format(
    base_endpoint=OAUTH2_BASE_ENDPOINT
)
OAUTH2_VERIFY_TLS = True
OAUTH2_TOKEN_CACHE_PATH = OAUTH2_CONFIG_PATH
