# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest

from pydidas.core import (Parameter, get_generic_parameter,
                          get_generic_param_collection, ParameterCollection)


class TestGetGenericParameter(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_get_param(self):
        _p = get_generic_parameter('first_file')
        self.assertIsInstance(_p, Parameter)

    def test_get_param__wrong_key(self):
        with self.assertRaises(KeyError):
            get_generic_parameter('there_should_be_no_such_key')

    def test_get_generic_param_collection__empty(self):
        _pc = get_generic_param_collection()
        self.assertIsInstance(_pc, ParameterCollection)

    def test_get_generic_param_collection(self):
        _keys = ['first_file', 'last_file']
        _pc = get_generic_param_collection(*_keys)
        for _key in _keys:
            self.assertIn(_key, _pc)


if __name__ == "__main__":
    unittest.main()
