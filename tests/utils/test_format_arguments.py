# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest

from pydidas.utils._format_str import format_str


class Test_format_str(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_format_arguments_only_args(self):
        _args = format_arguments('--test', ' a = 1', 'b=2')
        self.assertEqual(_args, ['--test', '-a', '1', '-b', '2'])

    def test_format_arguments_only_kwargs(self):
        _args = format_arguments(bool_test=True, c=3, s='string', f=6.6)
        self.assertEqual(_args, ['--bool_test', '-c', '3', '-s', 'string',
                                 '-f', '6.6'])

    def test_format_arguments_mixed(self):
        _args = format_arguments('--test', ' a = 1', 'b=2',
                                 bool_test=True, c=3, s='string', f=6.6)
        self.assertEqual(_args, ['--bool_test', '-c', '3', '-s', 'string',
                                 '-f', '6.6', '--test', '-a', '1', '-b', '2'])


if __name__ == "__main__":
    unittest.main()
