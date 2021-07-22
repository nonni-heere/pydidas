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
import time
import threading
import queue
import multiprocessing as mp

import numpy as np

from pydidas.multiprocessing import processor


def test_func(number, fixed_arg, fixed_arg2, kw_arg=0):
    return (number - fixed_arg) / fixed_arg2 + kw_arg


class _ProcThread(threading.Thread):

    """ Simple Thread to test blocking input / output. """

    def __init__(self, input_queue, output_queue, stop_queue, func):
        super().__init__()
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.stop_queue = stop_queue
        self.func = func

    def run(self):
       processor(self.input_queue, self.output_queue, self.stop_queue,
                 self.func)


class AppWithFunc:
    def __init__(self):
        self.offset = 5

    def test_func(self, number, fixed_arg, fixed_arg2, kw_arg=0):
        return (number - fixed_arg) / fixed_arg2 + kw_arg + self.offset


class Test_processor(unittest.TestCase):

    def setUp(self):
        self.input_queue = mp.Queue()
        self.output_queue = mp.Queue()
        self.stop_queue = mp.Queue()
        self.n_test = 20

    def tearDown(self):
        ...

    def put_ints_in_queue(self):
        for i in range(self.n_test):
            self.input_queue.put(i)
        self.input_queue.put(None)

    def get_results(self):
        _return = np.array([self.output_queue.get()
                            for i in range(self.n_test)])
        _res = _return[:,1]
        _input = _return[:,0]
        return _input, _res

    def test_run_plain(self):
        self.put_ints_in_queue()
        processor(self.input_queue, self.output_queue, self.stop_queue,
                  lambda x: x)
        _input, _output = self.get_results()
        self.assertTrue((_input == _output).all())

    def test_run_with_empty_queue(self):
        _thread = _ProcThread(self.input_queue, self.output_queue,
                              self.stop_queue, lambda x: x)
        _thread.start()
        time.sleep(0.1)
        self.input_queue.put(None)
        time.sleep(0.1)
        with self.assertRaises(queue.Empty):
            self.output_queue.get(timeout=0.1)

    def test_run_with_args_i(self):
        _args = (0, 1)
        self.put_ints_in_queue()
        processor(self.input_queue, self.output_queue, self.stop_queue,
                  test_func, *_args)
        _input, _output = self.get_results()
        _direct_out = test_func(_input, *_args)
        self.assertTrue((_output == _direct_out).all())

    def test_run_with_kwargs(self):
        _args = (0, 1)
        _kwargs = dict(kw_arg=12)
        self.put_ints_in_queue()
        processor(self.input_queue, self.output_queue, self.stop_queue,
                  test_func, *_args, **_kwargs)
        _input, _output = self.get_results()
        _direct_out = test_func(_input, *_args, **_kwargs)
        self.assertTrue((_output == _direct_out).all())

    def test_run_with_class_method(self):
        _args = (0, 1)
        self.put_ints_in_queue()
        app = AppWithFunc()
        processor(self.input_queue, self.output_queue, self.stop_queue,
                  app.test_func, *_args)
        _input, _output = self.get_results()
        _direct_out = app.test_func(_input, *_args)
        self.assertTrue((_output == _direct_out).all())


if __name__ == "__main__":
    unittest.main()
