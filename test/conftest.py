#  Copyright (c) 2015-2017 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

import distutils.spawn
import logging
import os
import random
import shutil
import string

import pytest

logging.getLogger('sh').setLevel(logging.WARNING)

pytest_plugins = ['helpers_namespace']


@pytest.fixture
def random_string(l=5):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(l))


@pytest.fixture()
def temp_dir(tmpdir, random_string, request):
    directory = tmpdir.mkdir(random_string)
    os.chdir(directory.strpath)

    def cleanup():
        try:
            shutil.rmtree(directory.strpath)
        except OSError:
            # LXC execute Molecule with sudo, which wreak havoc
            # on functional tests.
            pass

    request.addfinalizer(cleanup)

    return directory


def get_docker_executable():
    return not distutils.spawn.find_executable('docker')


def get_lxc_executable():
    return not distutils.spawn.find_executable('lxc')


def get_vagrant_executable():
    return not distutils.spawn.find_executable('vagrant')


def get_virtualbox_executable():
    return not distutils.spawn.find_executable('VBoxManage')


@pytest.helpers.register
def supports_docker():
    return pytest.mark.skipif(
        get_docker_executable(), reason='Docker not supported')


@pytest.helpers.register
def supports_lxc():
    return pytest.mark.skipif(get_lxc_executable(), reason='LXC not supported')


@pytest.helpers.register
def supports_vagrant_virtualbox():
    return pytest.mark.skipif(
        get_vagrant_executable() or get_virtualbox_executable(),
        reason='VirtualBox not supported')
