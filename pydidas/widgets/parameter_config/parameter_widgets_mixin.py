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

"""
Module with the ParameterWidgetsMixIn class used to edit plugin
Parameters.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ParameterWidgetsMixIn"]

from .parameter_config_widget import ParameterConfigWidget
from ...core import PydidasGuiError
from ..utilities import get_widget_layout_args


class ParameterWidgetsMixIn:
    """
    The ParameterWidgetsMixIn class includes methods which can be added
    to other classes without having to inherit from ParameterConfigWidget to
    avoid multiple inheritance from QtWidgets.QFrame.
    """

    def __init__(self):
        self.param_widgets = {}
        self.param_composite_widgets = {}

    def create_param_widget(self, param, **kwargs):
        """
        Add a name label and input widget for a specific parameter to the
        widget.

        Parameters
        ----------
        param : Parameter
            A Parameter class instance.
        **kwargs : dict
            Optional keyword arguments

        Keyword arguments
        -----------------
        gridPos : tuple, optional
            The grid position in the layout. The default is (-1, 0, 1, 1)
        width_total : int, optional
            The total width of the widget. The width of the IO widget is
            calculated from width_total, width_text, width_unit and linebreak.
        width_text : int, optional
            The width of the text field for the Parameter name. The default
            is 120.
        width_unit : int, optional
            The width of the text field for the Parameter unit. The default
            is 30.
        width_io : int, optional
            The width of the input widget. The default is 255 pixel.
        linebreak : bool, optional
            Keyword to toggle a line break between the text label and the
            input widget. The default is False.
        halign_io : QtCore.Qt.Alignment, optional
            The horizontal alignment for the input widget. The default is
            QtCore.Qt.AlignRight.
        halign_text : QtCore.Qt.Alignment, optional
            The horizontal alignment for the text (label) widget. The default
            is QtCore.Qt.AlignRight.
        valign_io : QtCore.Qt.Alignment, optional
            The vertical alignment for the input widget. The default is
            QtCore.Qt.AlignTop.
        valign_text : QtCore.Qt.Alignment, optional
            The vertical alignment for the text (label) widget. The default
            is QtCore.Qt.AlignTop.
        parent_widget : Union[QWidget, None], optional
            The widget to which the label is added. If None, this defaults
            to the calling widget, ie. "self". The default is None.
        """
        _parent = kwargs.get("parent_widget", self)
        _widget = ParameterConfigWidget(param, **kwargs)
        self.param_composite_widgets[param.refkey] = _widget
        self.param_widgets[param.refkey] = _widget.io_widget

        if _parent.layout() is None:
            raise PydidasGuiError("No layout set.")
        _layout_args = get_widget_layout_args(_parent, **kwargs)
        _parent.layout().addWidget(_widget, *_layout_args)

    def set_param_value_and_widget(self, key, value):
        """
        Update a parameter value both in the Parameter and the widget.

        This method will update the parameter referenced by <key> and
        update both the Parameter.value as well as the displayed widget
        entry.

        Parameters
        ----------
        key : str
            The reference key for the Parameter.
        value : object
            The new parameter value. This must be of the same type as the
            Parameter datatype.

        Raises
        ------
        KeyError
            If no parameter or widget has been registered with this key.
        """
        if key not in self.params or key not in self.param_widgets:
            raise KeyError(f'No parameter with key "{key}" found.')
        self.set_param_value(key, value)
        self.param_widgets[key].set_value(value)

    def toggle_param_widget_visibility(self, key, visible):
        """
        Toggle the visibility of widgets referenced with key.

        This method allows to show/hide the label and input widget for a
        parameter referenced with <key>.

        Parameters
        ----------
        key : str
            The reference key for the Parameter..
        visible : bool
            The boolean setting for the visibility.

        Raises
        ------
        KeyError
            If no widget has been registered with this key.
        """
        if key not in self.param_widgets:
            raise KeyError(f'No parameter with key "{key}" found.')
        self.param_composite_widgets[key].setVisible(visible)

    def update_widget_value(self, param_key, value):
        """
        Update the value stored in a widget without changing the Parameter.

        Parameters
        ----------
        param_key : str
            The Parameter reference key.
        value : object
            The value. The type depends on the Parameter's value.
        """
        self.param_widgets[param_key].set_value(value)
