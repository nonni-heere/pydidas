# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module with the processor function which can be used for iterating over
multiprocessing function calls."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['AppRunner']

import copy

from PyQt5 import QtCore

from pydidas.multiprocess.worker_controller import WorkerController
from pydidas.multiprocess.app_processor_func import app_processor
from pydidas.apps import BaseApp


class AppRunner(WorkerController):
    """
    The AppRunner is a subclassed WorkerController (QThread) which can
    spawn a number of processes to perform computations in parallel.

    The App runner requires a BaseApp (or subclass) instance with a
    defined method layout as defined in BaseApp.

    The AppRunner will

    Signals
    -------
    progress : QtCore.pyqtSignal
        This singal emits the current progress (0..1) in the computations,
        based on the number of returned results relative to the total tasks.
    results : QtCore.pyqtSignal
        The results as returned from the multiprocessing Processes.
    finished : QtCore.pyqtSignal
        This signal is emitted when the computations are finished. If the
        AppRunner is running headless, it needs to be connected to the
        app.exit slot to finish the event loop.
    final_app_state : QtCore.pyqtSignal
        This signal emits a copy of the App after all the calculations have
        been performed if it needs to be used in another context.
    """
    progress = QtCore.pyqtSignal(float)
    results = QtCore.pyqtSignal(int, object)
    finished = QtCore.pyqtSignal()
    final_app_state = QtCore.pyqtSignal(object)

    def __init__(self, app, n_workers=4):
        """
        Create a WorkerController.

        Parameters
        ----------
        n_workers : int, optional
            The number of spawned worker processes. The default is 4.
        """
        super().__init__(n_workers)
        self.__app = copy.copy(app)
        self.__check_app_is_set()
        self._processor['func'] = app_processor

    def call_app_method(self, method_name, *args, **kwargs):
        """
        Change a method of the app.

        Parameters
        ----------
        method_name : str
            The name of the Application.method.
        *args : type
            Any arguments which need to be passed to the method..
        **kwargs : kwargs
            Any keyword arguments which need to be passed to the method.

        Raises
        ------
        RuntimeError
            If the Application is currently running.

        Returns
        -------
        result : type
            The return object(s) from the App.method call.
        """
        self.__check_is_running()
        self.__check_app_method_name(method_name)
        method = getattr(self.__app, method_name)
        _result = method(*args, **kwargs)
        return _result

    def set_app_param(self, param_name, value):
        """
        Set a Parameter of the Application.

        Parameters
        ----------
        param_name : str
            The name of the Application Parameter.
        value : type
            The new value for the selected Parameter.
        """
        self.__check_app_is_set()
        self.__app.set_param_value(param_name, value)

    def _cycle_pre_run(self):
        """
        Perform pre-multiprocessing operations.

        This time slot is used to prepare the App by running the
        :my:meth:`app.multiprocessing_pre_run`, settings the tasks and
        starting the workers.
        """
        self.__app.multiprocessing_pre_run()
        self._processor['args'] = (self._queues['send'], self._queues['recv'],
                                   *self.__get_app_arguments())
        _tasks = self.__app.multiprocessing_get_tasks()
        self.add_tasks(_tasks)
        self.finalize_tasks()
        self.results.connect(self.__app.multiprocessing_store_results)
        self.progress.connect(self.__check_progress)
        self._create_and_start_workers()

    def _cycle_post_run(self):
        """
        Perform finishing operations of the App and close the multiprocessing
        Processes.
        """
        self._join_workers()
        self.__app.multiprocessing_post_run()
        self.final_app_state.emit(self.__app.copy())

    @QtCore.pyqtSlot(float)
    def __check_progress(self, progress):
        """
        Check the progress and send the signal to stop the loop if all
        results have been received.

        Parameters
        ----------
        progress : float
            The relative progress of the calculations.
        """
        if progress >= 1:
            self.suspend()
            self.stop()

    def __check_is_running(self):
        """Verify that the Thread is not actively running."""
        if self._flag_running:
            raise RuntimeError('Cannot call Application methods while the'
                               ' Application is running. Please call .stop()'
                               ' on the AppRunner first.')

    def __check_app_method_name(self, method_name):
        """Verify the Application has a method with the given name."""
        if not hasattr(self.__app, method_name):
            raise KeyError('The App does not have a method with name '
                           f'"{method_name}".')

    def __check_app_is_set(self):
        """
        Verify that the App passed to the AppRunner is a
        :py:class:`pydidas.apps.BaseApp`.
        """
        if not isinstance(self.__app, BaseApp):
            raise TypeError('Application is not an instance of BaseApp.'
                            ' Please set application first.')

    def __get_app_arguments(self):
        """Get the App arguments to pass to the processor."""
        return (self.__app.__class__, self.__app.params.get_copy(),
                self.__app.get_config())


if __name__ == '__main__':
    app = None
    @QtCore.pyqtSlot()
    def about_to_finish():
        """Terminate the headless app."""
        print('received finished signal')
        _qtapp = QtCore.QCoreApplication.instance()
        _qtapp.exit()

    @QtCore.pyqtSlot(object)
    def final_app(_app):
        global app
        app = _app


    from pydidas.apps.mp_test_app import MpTestApp
    import sys
    import time
    qt_app = QtCore.QCoreApplication(sys.argv)
    runner = AppRunner(MpTestApp(), 8)
    runner.set_app_param('hdf_first_image_num', 10)
    runner.finished.connect(about_to_finish)
    runner.final_app_state.connect(final_app)
    runner.start()
    t0 = time.time()
    qt_app.exec_()
    print(time.time() - t0)
