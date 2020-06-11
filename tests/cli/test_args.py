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
from coaclient.cli import Actions, Arg


def test_actions():
    # Actions STORE
    assert Actions.STORE == "store"
    assert isinstance(Actions.STORE, str)
    # Actions STORE_CONST
    assert Actions.STORE_CONST == "store_const"
    assert isinstance(Actions.STORE_CONST, str)
    # Actions STORE_TRUE
    assert Actions.STORE_TRUE == "store_true"
    assert isinstance(Actions.STORE_TRUE, str)
    # Actions STORE_FALSE
    assert Actions.STORE_FALSE == "store_false"
    assert isinstance(Actions.STORE_FALSE, str)
    # Actions APPEND
    assert Actions.APPEND == "append"
    assert isinstance(Actions.APPEND, str)
    # Actions APPEND_CONST
    assert Actions.APPEND_CONST == "append_const"
    assert isinstance(Actions.APPEND_CONST, str)
    # Actions COUNT
    assert Actions.COUNT == "count"
    assert isinstance(Actions.COUNT, str)
    # Actions VERSION
    assert Actions.VERSION == "version"
    assert isinstance(Actions.VERSION, str)
    # Actions HELP
    assert Actions.HELP == "help"
    assert isinstance(Actions.HELP, str)


def test_arg():
    arg = Arg(flags=('-f', '--flag'))
    assert hasattr(arg, "__dataclass_fields__")
    assert arg.flags == ('-f', '--flag')
    assert arg.action == Actions.STORE
    assert arg.required is False
