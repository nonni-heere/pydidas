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
Module with the WorkflowEditFrame which is used to create the WorkflowTree.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["WorkflowEditFrame"]

from functools import partial

from qtpy import QtCore, QtWidgets

from ...plugins import PluginCollection
from ...workflow import WorkflowTree
from ...workflow.workflow_tree_io import WorkflowTreeIoMeta
from ..managers import WorkflowTreeEditManager
from .builders import WorkflowEditFrameBuilder

TREE = WorkflowTree()
PLUGIN_COLLECTION = PluginCollection()
WORKFLOW_EDIT_MANAGER = WorkflowTreeEditManager()


@QtCore.Slot(int, str)
def workflow_add_plugin_at_parent(parent_id, name):
    """
    Get the signal that a new Plugin has been selected and must be added
    to the WorkflowTree and forward it to the WorkflowTreeEditManager.

    Parameters
    ----------
    parent_id : int
        The parent node id. Because of Qt's slot signature, a -1 is used for
        no parent. If -1, the node will be added to the WorkflowTree's
        active node.
    name : str
        The name of the new Plugin.
    """
    if parent_id == -1:
        parent_id = None
    WORKFLOW_EDIT_MANAGER.add_new_plugin_node(name, parent_node_id=parent_id)


class WorkflowEditFrame(WorkflowEditFrameBuilder):
    """
    The WorkflowEditFrame includes three major objects:
        a. The editing canvas which shows the WorkflowTree structure.
        b. A Plugin information and selection box to browse all available
           plugins and add them to the WorkflowTree.
        c. An editing panel to modify the Parameters for the individual
           plugins.
    """

    menu_title = "Workflow editing"
    menu_entry = "Workflow processing/Workflow editing"
    menu_icon = "qta::ph.share-network-fill"

    def __init__(self, parent=None, **kwargs):
        WorkflowEditFrameBuilder.__init__(self, parent, **kwargs)

    def connect_signals(self):
        """
        Connect all signals and slots in the frame.
        """
        self._widgets["plugin_collection"].sig_add_plugin_to_tree.connect(
            partial(workflow_add_plugin_at_parent, -1)
        )
        self._widgets["plugin_collection"].sig_replace_plugin.connect(
            self.workflow_replace_plugin
        )
        self._widgets["plugin_collection"].sig_append_to_specific_node.connect(
            workflow_add_plugin_at_parent
        )
        WORKFLOW_EDIT_MANAGER.sig_plugin_selected.connect(self.configure_plugin)
        WORKFLOW_EDIT_MANAGER.update_qt_canvas(self._widgets["workflow_canvas"])
        self._widgets["but_save"].clicked.connect(self.save_tree_to_file)
        self._widgets["but_load"].clicked.connect(self.load_tree_from_file)

    @QtCore.Slot(str)
    def workflow_replace_plugin(self, plugin_name):
        """
        Get the signal that the active node's Plugin should be replaced by a new
        Plugin class.

        Parameters
        ----------
        plugin_name : str
            The name of the new Plugin.
        """
        _plugin = PLUGIN_COLLECTION.get_plugin_by_plugin_name(plugin_name)()
        TREE.active_node.plugin = _plugin
        self.configure_plugin(TREE.active_node_id)
        WORKFLOW_EDIT_MANAGER._node_widgets[TREE.active_node_id].setText(plugin_name)

    @QtCore.Slot(int)
    def configure_plugin(self, node_id):
        """
        Get the signal that a new Plugin has been selected to be edited and
        pass the information to the PluginEditCanvas.

        Parameters
        ----------
        node_id : int
            The Plugin node ID.
        """
        if node_id == -1:
            self._widgets["plugin_edit_canvas"].clear_layout()
            return
        plugin = TREE.nodes[node_id].plugin
        self._widgets["plugin_edit_canvas"].configure_plugin(node_id, plugin)
        self._widgets["plugin_edit_canvas"].sig_new_label.connect(
            WORKFLOW_EDIT_MANAGER.new_node_label_selected
        )

    def save_tree_to_file(self):
        """
        Open a QFileDialog to geta save name and export the WorkflowTree to
        the selected file with the specified format.
        """
        _file_selection = WorkflowTreeIoMeta.get_string_of_formats()
        fname = QtWidgets.QFileDialog.getSaveFileName(
            self, "Name of file", None, _file_selection
        )[0]
        if fname in ["", None]:
            return
        TREE.export_to_file(fname, overwrite=True)

    def load_tree_from_file(self):
        """
        Open a Qdialog to select a filename, read the file and import an
        existing WorkflowTree from the retrieved information.
        """
        _file_selection = WorkflowTreeIoMeta.get_string_of_formats()
        _func = QtWidgets.QFileDialog.getOpenFileName
        fname = _func(self, "Name of file", None, _file_selection)[0]
        if fname in ["", None]:
            return
        TREE.import_from_file(fname)
        WORKFLOW_EDIT_MANAGER.update_from_tree(reset_active_node=True)

    def export_state(self):
        """
        Export the state of the Frame for saving.

        Returns
        -------
        frame_index : int
            The frame index which can be used as key for referencing the state.
        information : dict
            A dictionary with all the information required to export the
            frame's state.
        """
        _params = self.get_param_values_as_dict(filter_types_for_export=True)
        _widgets = {
            _key: _w.geometry().getCoords() for _key, _w in self._widgets.items()
        }
        return (self.frame_index, {"params": _params, "widgets": _widgets})

    def restore_state(self, state):
        """
        Restore the frame's state from stored information.

        The default implementation in the BaseFrame will update all Parameters
        (and associated widgets) and restore the visibility of all widgets. If the
        frame has not yet been built, the state information is only stored internally
        and not yet applied. It will be applied at the next frame activation.

        Parameters
        ----------
        state : dict
            A dictionary with 'params' and 'visibility' keys and the respective
            information for both.
        """
        if not self._config["built"]:
            self._config["state"] = state
            return
        super().restore_state(state)
        for _key, _coords in state["widgets"].items():
            self._widgets[_key].setGeometry(*_coords)
        WORKFLOW_EDIT_MANAGER.update_from_tree(reset_active_node=True)

    @QtCore.Slot(int)
    def frame_activated(self, index):
        """
        Received a signal that a new frame has been selected.

        This method checks whether the selected frame is the current class
        and if yes, it will call some updates.

        Parameters
        ----------
        index : int
            The index of the newly activated frame.
        """
        super().frame_activated(index)
        if self.frame_index == index:
            WORKFLOW_EDIT_MANAGER.update_from_tree()
