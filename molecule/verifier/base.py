#  Copyright (c) 2015-2018 Cisco Systems, Inc.
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

import os

import abc
import molecule

from molecule import util
from molecule.verifier.lint import flake8
from molecule.verifier.lint import precommit
from molecule.verifier.lint import rubocop
from molecule.verifier.lint import yamllint
from molecule.verifier.lint import ansible_lint


class Verifier(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, config=None):
        """
        Base initializer for all :ref:`Verifier` classes.

        :param config: An instance of a Molecule config.
        :returns: None
        """
        self._config = config
        self.default_linter = 'ansible-lint'

    @abc.abstractproperty
    def name(self):  # pragma: no cover
        """
        Name of the verifier and returns a string.

        :returns: str
        """
        pass

    @abc.abstractproperty
    def default_options(self):  # pragma: no cover
        """
        Default CLI arguments provided to ``cmd`` and returns a dict.

        :return: dict
        """
        pass

    @abc.abstractproperty
    def default_env(self):  # pragma: no cover
        """
        Default env variables provided to ``cmd`` and returns a dict.

        :return: dict
        """
        pass

    @abc.abstractmethod
    def execute(self):  # pragma: no cover
        """
        Executes ``cmd`` and returns None.

        :return: None
        """
        pass

    @abc.abstractmethod
    def schema(self):  # pragma: no cover
        """
        Returns validation schema.

        :return: None
        """
        pass

    @property
    def enabled(self):
        return self._config.config['verifier']['enabled']

    @property
    def directory(self):
        return os.path.join(
            self._config.scenario.directory,
            self._config.config['verifier']['directory'],
        )

    @property
    def options(self):
        return util.merge_dicts(
            self.default_options, self._config.config['verifier']['options']
        )

    @property
    def env(self):
        return util.merge_dicts(
            self.default_env, self._config.config['verifier']['env']
        )

    @property
    @util.lru_cache()
    def lint(self):
        lint_name = self._config.config['verifier']['lint']['name']
        if lint_name == 'flake8':
            return flake8.Flake8(self._config)
        if lint_name == 'pre-commit':
            return precommit.PreCommit(self._config)
        if lint_name == 'rubocop':
            return rubocop.RuboCop(self._config)
        if lint_name == 'yamllint':
            return yamllint.Yamllint(self._config)
        if lint_name == 'ansible-lint':
            return ansible_lint.AnsibleLint(self._config)

    def __eq__(self, other):
        return str(self) == str(other)

    def __lt__(self, other):
        return str.__lt__(str(self), str(other))

    def __hash__(self):
        return self.name.__hash__()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def template_dir(self):
        p = os.path.abspath(
            os.path.join(
                os.path.dirname(molecule.__file__),
                "cookiecutter",
                "scenario",
                "verifier",
                self.name,
            )
        )
        return p
