"""Tests utils"""
# !/usr/bin/env python
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

import logging

from coaclient import main
from coaclient import utils


# Set up mocking of the `open` call. See http://www.ichimonji10.name/blog/6/


def test_set_logging_level_none_specified():
    """Test logging level not specified"""
    parser = main.build_parser()
    args = parser.parse_args('version'.split())
    utils.set_logging_level(args)
    assert logging.getLogger().getEffectiveLevel() == logging.INFO or \
        logging.getLogger().getEffectiveLevel() == logging.NOTSET
