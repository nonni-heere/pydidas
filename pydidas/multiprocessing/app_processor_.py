# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the app_processor function which can be used for iterating over
multiprocessing calls to a pydidas Application.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["app_processor"]

import queue
import time
from multiprocessing import Queue

from ..core import ParameterCollection
from ..core.utils import LOGGING_LEVEL, pydidas_logger


logger = pydidas_logger()
logger.setLevel(LOGGING_LEVEL)


def app_processor(
    input_queue: Queue,
    output_queue: Queue,
    stop_queue: Queue,
    aborted_queue: Queue,
    app: type,
    app_params: ParameterCollection,
    app_config: dict,
    **kwargs: dict,
):
    """
    Start a loop to process function calls on individual frames.

    This function starts a while loop to call the supplied function with
    indices supplied by the queue. Results will be written to the output
    queue in a format [input_arg, results]

    Parameters
    ----------
    input_queue : multiprocessing.Queue
        The input queue which supplies the processor with indices to be
        processed.
    output_queue : multiprocessing.Queue
        The queue for transmissing the results to the controlling thread.
    stop_queue : multiprocessing.Queue
        The queue for sending a termination signal to the worker.
    aborted_queue : multiprocessing.Queue
        The queue which is used by the processor to signal the calling
        thread that it has aborted its cycle.
    app : type
        The Application class to be called in the process. The App must have a
        multiprocessing_func method.
    app_params : ParameterCollection
        The App ParameterCollection used for creating the app.
    app_config : dict
        The dictionary which is used for overwriting the app._config
        dictionary.
    **kwargs : dict
        Any keyword arguments passed to the app processor.
    """
    _wait_for_output = kwargs.get("wait_for_output_queue", True)
    _app_carryon = True
    logger.debug("Started process")
    _app = app(app_params, slave_mode=True)
    _app._config = app_config
    _app.multiprocessing_pre_run()
    while True:
        # check for stop signal
        try:
            stop_queue.get_nowait()
            logger.debug("Received stop queue signal")
            aborted_queue.put(1)
            break
        except queue.Empty:
            pass
        # run processing step
        if _app_carryon:
            try:
                _arg = input_queue.get_nowait()
            except queue.Empty:
                time.sleep(0.005)
                continue
            if _arg is None:
                logger.debug("Received queue empty signal in input queue.")
                output_queue.put([None, None])
                break
            logger.debug('Received item "%s" from queue' % _arg)
            _app.multiprocessing_pre_cycle(_arg)
        _app_carryon = _app.multiprocessing_carryon()
        if _app_carryon:
            logger.debug("Starting computation of item %s" % _arg)
            _results = _app.multiprocessing_func(_arg)
            output_queue.put([_arg, _results])
            logger.debug("Finished computation of item %s" % _arg)
    logger.debug("Worker finished with all tasks. Waiting for output queue to empty.")
    while _wait_for_output and not output_queue.empty():
        time.sleep(0.05)
    logger.debug("Output queue empty. Worker shutting down.")
