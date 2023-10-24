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
The gui.mixins subpackage includes gui-specific mixin-classes to extend
the functionality of other classes.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


# import __all__ items from modules:
from .silx_plotwindow_mixin import *
from .view_results_mixin import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import silx_plotwindow_mixin

__all__.extend(silx_plotwindow_mixin.__all__)
del silx_plotwindow_mixin

from . import view_results_mixin

__all__.extend(view_results_mixin.__all__)
del view_results_mixin
