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
from coaclient.cli import Arg, Actions
from coaclient.log import LogLevels, add_logging, setup_logging
from tests import empty_cli_factory, arguments
import logging


def test_log_levels():
    # test cases for static method get_level_name
    assert LogLevels.get_level_name("INFO") == LogLevels.INFO, \
        f"LogLevels id for \"INFO\" level should be: {LogLevels.INFO}"
    assert LogLevels.get_level_name("DEBUG") == LogLevels.DEBUG, \
        f"LogLevels id for \"DEBUG\" level should be: {LogLevels.DEBUG}"
    assert LogLevels.get_level_name("WARNING") == LogLevels.WARNING, \
        f"LogLevels id for \"WARNING\" level should be: {LogLevels.WARNING}"
    assert LogLevels.get_level_name("ERROR") == LogLevels.ERROR, \
        f"LogLevels id for \"ERROR\" level should be: {LogLevels.ERROR}"
    assert LogLevels.get_level_name("CRITICAL") == LogLevels.CRITICAL, \
        f"LogLevels id for \"CRITICAL\" level should be: {LogLevels.CRITICAL}"

    assert LogLevels.get_level_name(LogLevels.INFO) == "INFO", \
        f"LogLevels name for id \"{LogLevels.INFO}\" level should be: INFO"
    assert LogLevels.get_level_name(LogLevels.DEBUG) == "DEBUG", \
        f"LogLevels name for id \"{LogLevels.DEBUG}\" level should be: DEBUG"
    assert LogLevels.get_level_name(LogLevels.WARNING) == "WARNING", \
        f"LogLevels name for id \"{LogLevels.WARNING}\" level should be: WARNING"
    assert LogLevels.get_level_name(LogLevels.ERROR) == "ERROR", \
        f"LogLevels name for id \"{LogLevels.ERROR}\" level should be: ERROR"
    assert LogLevels.get_level_name(LogLevels.CRITICAL) == "CRITICAL", \
        f"LogLevels name for id \"{LogLevels.CRITICAL}\" level should be: CRITICAL"

    # test cases for class method log levels
    assert LogLevels.log_levels() == [
        "INFO", "WARNING", "ERROR", "DEBUG", "CRITICAL"
    ]


def test_add_logging():
    # Make base CLI Factory with main empty parser
    cli = empty_cli_factory()
    # Add logging to the main parser
    add_logging(cli)
    # test cases for add_logging
    # 1. Check log_level argument
    log_level_arg = cli._args.get('log_level')
    assert log_level_arg is not None
    assert isinstance(log_level_arg, Arg)
    assert log_level_arg.default == LogLevels.get_level_name(LogLevels.INFO)
    assert log_level_arg.choices == LogLevels.log_levels()
    # 2. Check silence_urllib3 argument
    silence_urllib3_arg = cli._args.get('silence_urllib3')
    assert silence_urllib3_arg is not None
    assert isinstance(silence_urllib3_arg, Arg)
    assert silence_urllib3_arg.action == Actions.STORE_TRUE
    # 3. Check the arguments add to main parser
    assert 'log_level' in cli._parser.args
    assert 'silence_urllib3' in cli._parser.args
    # 4. Check if setup default method for setup_logging in main parser
    assert 'setup_logging' in cli.parser.defaults
    assert setup_logging == cli.parser.defaults.get('setup_logging')


def test_setup_log():
    # test cases for setup log method
    test_cases = (
        dict(log_level="INFO", silence_urllib3=False),
        dict(log_level="DEBUG", silence_urllib3=False),
        dict(log_level="WARNING", silence_urllib3=False),
        dict(log_level="ERROR", silence_urllib3=False),
        dict(log_level="CRITICAL", silence_urllib3=False),
        dict(log_level="INFO", silence_urllib3=True),
        dict(log_level="DEBUG", silence_urllib3=True),
        dict(log_level="WARNING", silence_urllib3=True),
        dict(log_level="ERROR", silence_urllib3=True),
        dict(log_level="CRITICAL", silence_urllib3=True)
    )

    for test_case in test_cases:
        # test arguments
        args = arguments(**test_case)
        assert args.log_level == test_case["log_level"]
        assert args.silence_urllib3 == test_case["silence_urllib3"]
        # test setup_logging
        setup_logging(args)
        assert logging.getLogger().level == LogLevels.get_level_name(
            test_case["log_level"]
        )
        assert logging.getLogger(
            "requests.packages.urllib3"
        ).level == LogLevels.WARNING
