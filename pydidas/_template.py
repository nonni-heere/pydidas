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

"""Module with the WorkflowPluginWidget which is used to create the workflow
tree."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

from PyQt5 import QtWidgets, QtCore
from pydidas.config import gui_constants, qt_presets


class _PluginDescriptionField(QtWidgets.QTextEdit):
    """
    Text edit to show the description of the plugin and its parameters.
    """

    def __init__(self, parent=None, **params):
        """
        Create the _PluginDescriptionField.

        Parameters
        ----------
        parent : QWidget, optional
            The Qt parent widget. The default is None.
        readOnly : bool, optional
            Flag to set the field to read only. The default is True.
        minimumWidth : Union[int, None], optional
            The minimum width of the widget. If None, no minimum width will be
            set for the widget. The default is 500.
        fixedWidth : Union[int, None], optional
            A fixed width for the widget. If None, no fixedWidth will be set.
            The default is None.
        minimumHeight : Union[int, None], optional
            The minimum Height of the widget. If None, no minimum height will
            be set for the widget. The default is None.
        fixedHeight : Union[int, None], optional
            A fixed height for the widget. If None, no fixedHeight will be set.
            The default is None.


        Returns
        -------
        None.

        """
        super().__init__(parent)
        _params = {'readOnly': params.get('readOnly', True),
                   'fixedWidth': params.get('fixedWidth', None),
                   'minimumWidth': params.get('minimumWidth', 500),
                   'fixedHeight': params.get('fixedHeight', None),
                   'minimumHeight': params.get('minimumHeight', None)}
        self.setAcceptRichText(True)
        self.setReadOnly(_params['readOnly'])
        for _param, _func  in zip(
                ['fixedWidth', 'minimumWidth', 'fixedHeight', 'minimumHeight'],
                [self.setFixedWidth, self.setMinimumWidth,
                 self.setFixedHeight, self.setMinimumHeight]):
            if _params[_param] is not None:
                _func(_params[_param])
        self.setMinimumWidth(500)

    def setText(self, text, title=None):
        """
        Display information about a plugin.

        This widget accepts both a single text entry and a list of entries
        for the text. A list of entries will be converted to a single text
        according to

        Parameters
        ----------
        text : str or list of str.
            The text to be displayed.
        title : str, optional
            The title. The default is None.

        Returns
        -------
        None.
        """
        if isinstance(text, str):
            super().setText(text)
        elif isinstance(text, list):
            super().setText('')
            if title:
                self.setFontPointSize(14)
                self.setFontWeight(75)
                self.append(f'Plugin description: {title}')
            self.setFontPointSize(10)
            self.append('')

            for key, item in text:
                self.setFontWeight(75)
                self.append(key + ':')
                self.setFontWeight(50)
                self.append(' ' * 4 + item if key != 'Parameters' else item)
        self.verticalScrollBar().triggerAction(
            QtWidgets.QScrollBar.SliderToMinimum
        )
