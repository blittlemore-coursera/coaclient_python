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
CoaClient base exception
"""
__all__ = (
    "CoaClientBaseException",
)


class CoaClientBaseException(Exception):
    """ Base exception class for custom exception """
    _STR = None

    def __init__(self, message: str, *args):
        self.message = message
        super().__init__(message, *args)

    def __str__(self):
        if self._STR is None:
            return super().__str__()
        return self._STR.format(
            message=self.message
        )
