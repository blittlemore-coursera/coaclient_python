"""Test commands"""
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
import _pickle
import argparse
# Set up mocking of the `open` call. See http://www.ichimonji10.name/blog/6/
import builtins
import re
import time
from configparser import ConfigParser

from mock import mock_open, MagicMock, patch

from coaclient import oauth2


def test_compute_cache_filename_args_override():
    """Test compute cache file name args override"""
    args = argparse.Namespace()
    args.token_cache_file = '/tmp/cache/override_cache.pickle'
    args.client_id = 'client_id'
    args.client_secret = 'fake-secret'
    args.scopes = 'fake scopes'
    cfg = ConfigParser()
    cfg.add_section('oauth2')
    cfg.set('oauth2', 'token_cache_base', '/tmp/not_cache')
    assert oauth2.build_oauth2(
        'my_app', args, cfg
    ).token_cache_file == '/tmp/cache/override_cache.pickle'


def test_compute_cache_filename():
    """Test compute cache filename"""
    args = argparse.Namespace()
    args.client_id = 'client_id'
    args.client_secret = 'fake-secret'
    args.scopes = 'fake scopes'
    cfg = ConfigParser()
    cfg.add_section('oauth2')
    cfg.set('oauth2', 'token_cache_base', '/tmp/cache')
    assert oauth2.build_oauth2(
        'my_app', args, cfg
    ).token_cache_file == '/tmp/cache/my_app_oauth2_cache.pickle'


def test_cache_filename_sanitized():
    """Test cache filename sanitized"""
    args = argparse.Namespace()
    args.client_id = 'client_id'
    args.client_secret = 'fake-secret'
    args.scopes = 'fake scopes'
    cfg = ConfigParser()
    cfg.add_section('oauth2')
    cfg.set('oauth2', 'token_cache_base', '/tmp/cache')
    print(oauth2.build_oauth2('@weird$app name', args, cfg).token_cache_file)
    assert oauth2.build_oauth2(
        '@weird$app name', args, cfg
    ).token_cache_file == '/tmp/cache/_weird_app_name_oauth2_cache.pickle'


def test_compute_cache_filename_expanded_path():
    """Test compute cache filename expanded path"""
    args = argparse.Namespace()
    args.client_id = 'client_id'
    args.client_secret = 'fake-secret'
    args.scopes = 'fake scopes'
    cfg = ConfigParser()
    cfg.add_section('oauth2')
    cfg.set('oauth2', 'token_cache_base', '~/.coursera')
    computed = oauth2.build_oauth2('my_app', args, cfg).token_cache_file
    assert '~' not in computed, 'Computed contained "~": %s' % computed


def test_compute_cache_filename_path_no_double_slash():
    """Test compute cache filename path no double slash"""
    args = argparse.Namespace()
    args.client_id = 'client_id'
    args.client_secret = 'fake-secret'
    args.scopes = 'fake scopes'
    cfg = ConfigParser()
    cfg.add_section('oauth2')
    cfg.set('oauth2', 'token_cache_base', '~/.coursera/')
    computed = oauth2.build_oauth2('my_app', args, cfg).token_cache_file
    assert '//' not in computed, 'Computed contained "//": %s' % computed


def test_compute_cache_filename_expanded_path_overrides():
    """Test compute cache filename overrides expanded path"""
    args = argparse.Namespace()
    args.token_cache_file = '~/.coursera/override_cache.pickle'
    args.client_id = 'client_id'
    args.client_secret = 'fake-secret'
    args.scopes = 'fake scopes'
    cfg = ConfigParser()
    cfg.add_section('oauth2')
    cfg.set('oauth2', 'token_cache_base', '~/.coursera')
    computed = oauth2.build_oauth2('my_app', args, cfg).token_cache_file
    assert '~' not in computed, 'Computed contained "~": %s' % computed
    assert 'override_cache.pickle' in computed, 'Computed was not overridden!'


def test_check_cache_types():
    """Test cache types check"""
    # test cases are tuples of:
    # (name, cache_value, expected)
    test_cases = [
        ('basic dict', {}, False),
        ('basic array', [], False),
        ('basic int', 3, False),
        ('populated dict', {'token': 'asdfg', 'expires': 12345.0}, True)
    ]
    for test_case in test_cases:
        check_cache_types_impl.description = (
            'test_check_cache_types: %s' % test_case[0]
        )
        yield check_cache_types_impl, test_case[1], test_case[2]


def check_cache_types_impl(cache_type, should_be_allowed):
    """Check cache types"""
    oauth2_client = oauth2.CourseraOAuth2(
        'id', 'secret', 'fake scopes', '/cache.file'
    )
    result = oauth2_client._check_token_cache_type(cache_type)
    assert result == should_be_allowed, 'Got %s. Expected: %s' % {
        result, should_be_allowed
    }


def test_load_configuration():
    """Check load configuration"""
    cfg = oauth2.configuration()
    assert cfg.get('oauth2', 'hostname') == 'localhost', 'hostname incorrect'
    assert cfg.getint('oauth2', 'port') == 9876, 'oauth2.port not correct'
    print(cfg.get('oauth2', 'api_endpoint'))
    assert cfg.get(
        'oauth2', 'api_endpoint'
    ) == 'https://api.coursera.org', 'oauth2.api_endpoint incorrect'
    assert cfg.getboolean('oauth2', 'verify_tls'), 'oauth2.verify_tls wrong'


def test_expired_token_serialization():
    """Test serialization of expired token"""
    authorizer = oauth2.CourseraOAuth2Auth(token='asdf', expires=time.time())
    exception = oauth2.ExpiredToken(authorizer)
    assert len("%s" % exception) > 0


def test_authorizer_throws_when_expired():
    """Test authorizer throws an exception when token expired"""
    authorizer = oauth2.CourseraOAuth2Auth(
        token='asdf', expires=time.time() - 10
    )
    fake_request = MagicMock()
    try:
        authorizer(fake_request)
    except oauth2.ExpiredToken:
        pass
    else:
        assert False, 'authorizer should have thrown an exception'


def test_authorizer_does_not_throw_when_not_expired():
    """Test there is not exception when token is not expired"""
    authorizer = oauth2.CourseraOAuth2Auth(
        token='asdf', expires=time.time() + 10
    )
    fake_request = MagicMock()
    authorizer(fake_request)


def test_build_authorization_url():
    """Test build authorization url"""
    oauth2_client = oauth2.CourseraOAuth2(
        'my_fake_client_id', 'my_fake_secret', 'view_profile', '/cache.file'
    )

    state_token = 'my_fake_state_token'

    actual = oauth2_client._build_authorizaton_url(state_token)

    expected_url = {
        'https://accounts.coursera.org/oauth2/v1/auth',
        'access_type=offline',
        'state=my_fake_state_token',
        'redirect_uri=http%3A%2F%2Flocalhost%3A9876%2Fcallback',
        'response_type=code',
        'client_id=my_fake_client_id',
        'scope=view_profile'
    }
    actual_splitted = set(re.split('[&?]', actual))

    assert expected_url == actual_splitted, 'Got unexpected URL: %s %s' % (
        actual_splitted, expected_url
    )


def test_loading_cache():
    """Test loading cache"""
    valid_tokens = {
        'token': u'CiCptJ_07TeNA',
        'expires': 1438815118.228845,
        'refresh': u'STLuX5'
    }

    test_cases = [
        ('valid_tokens', _pickle.dumps(valid_tokens), valid_tokens),
        ('invalid pickle', _pickle.dumps(valid_tokens)[5:], None),
        ('garbage', b';lkajsdf;lkjasdlfk;j', None),
        ('bad object', _pickle.dumps({'weird': 'stuff'}), None),
    ]

    for test_case in test_cases:
        # loading_cache_checker.description = test_case[0]
        yield loading_cache_checker, test_case[1], test_case[2]


def loading_cache_checker(read_data, expected):
    """Checker of cache loading"""
    open_ = mock_open(read_data=read_data + b'\n')
    open_().readlines.return_value = read_data.split(b'\n')
    open_().readline.side_effect = read_data.split(b'\n')
    with patch.object(builtins, 'open', open_, create=True):
        oauth2_instance = oauth2.CourseraOAuth2(
            'id', 'secret', 'scopes', '/cache.file')
        token_cache = oauth2_instance.token_cache
        assert token_cache == expected, 'Token cache was: %s' % token_cache
