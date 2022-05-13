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
Module with various utility functions for widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = [
    "delete_all_items_in_layout",
    "apply_font_properties",
    "apply_widget_properties",
    "create_default_grid_layout",
    "get_pyqt_icon_from_str_reference",
]


from qtpy import QtWidgets, QtCore, QtGui
import qtawesome

from ..core.constants import STANDARD_FONT_SIZE


def delete_all_items_in_layout(layout):
    """
    Function to recursively delete items in a QLayout.

    Parameters
    ----------
    layout : QLayout
        The layout to be cleared.
    """
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            else:
                delete_all_items_in_layout(item.layout())


def _get_args_as_list(args):
    """
    Format the input arguments to an interable list to be passed as *args.

    Parameters
    ----------
    args : object
        Any input

    Returns
    -------
    args : Union[tuple, list, set]
        The input arguments formatted to a iterable list.
    """
    if not isinstance(args, (tuple, list, set)):
        args = [args]
    return args


def apply_widget_properties(obj, **kwargs):
    """
    Set Qt widget properties from a supplied dict.

    This function takes a dictionary (ie. keyword arguments) and iterates
    through all keys. Keys will be interpreted in Qt style: A "property: 12"
    entry in the dictionary will verify that the widget has a "setProperty"
    method and will then call "obj.setProperty(12)". The verificiation that
    the methods exist allows this function to take the full kwargs of any
    object without the need to filter out non-related keys.

    Parameters
    ----------
    widget : QtWidgets.QWidget
        Any QWidget.
    **kwargs : dict
        A dictionary with properties to be set.
    """
    for _key in kwargs:
        _name = f"set{_key[0].upper()}{_key[1:]}"
        if hasattr(obj, _name):
            _func = getattr(obj, _name)
            _func(*_get_args_as_list(kwargs.get(_key)))


def apply_font_properties(fontobj, **kwargs):
    """
    Set font properties from a supplied dict.

    This function takes a dictionary (ie. keyword arguments) and iterates
    through all keys. Keys will be interpreted in Qt style: A "property: 12"
    entry in the dictionary will verify that the font object  has a
    "setProperty" method and will then call "fontobj.setProperty(12)". The
    verificiation that methods exist allows this function to take the full
    kwargs of any object without the need to filter out non-related keys.

    Parameters
    ----------
    fontobj : QObject
        Any QFont
    **kwargs : dict
        A dictionary with properties to be set.
    """
    if "fontsize" in kwargs and "pointSize" not in kwargs:
        kwargs["pointSize"] = kwargs.get("fontsize", STANDARD_FONT_SIZE)
    for _key in kwargs:
        _name = f"set{_key[0].upper()}{_key[1:]}"
        if hasattr(fontobj, _name):
            _func = getattr(fontobj, _name)
            _func(*_get_args_as_list(kwargs.get(_key)))


def create_default_grid_layout():
    """
    Create a QGridLayout with default parameters.

    The default parameters are

        - vertical spacing : 5
        - horizontal spacing : 5
        - alignment : left | top

    Returns
    -------
    layout : QGridLayout
        The layout.
    """
    _layout = QtWidgets.QGridLayout()
    _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    _layout.setHorizontalSpacing(5)
    _layout.setVerticalSpacing(5)
    return _layout


def get_pyqt_icon_from_str_reference(ref_string):
    """
    Get a QIcon from the reference string.

    Three types of strings can be processsed:
        1. References to a qtawesome icon. The reference must be preceeded
           by 'qta::'.
        2. A reference number of a QStandardIcon, preceeded by a 'qt-std::'.
        3. A reference to a image file in the file system. This must be
           preceeded by 'path::'.

    Parameters
    ----------
    ref_string : str
        The reference string for the icon.

    Raises
    ------
    TypeError
        If no correct preceeding type has been found.

    Returns
    -------
    QtGui.QIcon
        The icon

    """
    _type, _ref = ref_string.split("::")
    if _type == "qta":
        _menu_icon = qtawesome.icon(_ref)
    elif _type == "qt-std":
        _num = int(_ref)
        app = QtWidgets.QApplication.instance()
        _menu_icon = app.style().standardIcon(_num)
    elif _type == "path":
        _menu_icon = QtGui.QIcon(_ref)
    else:
        raise TypeError("Cannot interpret the string reference for " "the menu icon.")
    return _menu_icon
