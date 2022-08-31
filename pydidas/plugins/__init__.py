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
The pydidas.plugins subpackage includes the base classes for plugins as well as the
PluginCollection singleton which holds all registered plugins and allows to
get new instances of these plugins.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .base_input_plugin import *
from .base_input_plugin_1d import *
from .base_output_plugin import *
from .base_plugin import *
from .base_proc_plugin import *
from .plugin_collection import *
from .plugin_getter_ import *
from .pyfai_integration_base import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import base_input_plugin

__all__.extend(base_input_plugin.__all__)
del base_input_plugin

from . import base_input_plugin_1d

__all__.extend(base_input_plugin_1d.__all__)
del base_input_plugin_1d

from . import base_output_plugin

__all__.extend(base_output_plugin.__all__)
del base_output_plugin

from . import base_plugin

__all__.extend(base_plugin.__all__)
del base_plugin

from . import base_proc_plugin

__all__.extend(base_proc_plugin.__all__)
del base_proc_plugin

from . import plugin_collection

__all__.extend(plugin_collection.__all__)
del plugin_collection

from . import plugin_getter_

__all__.extend(plugin_getter_.__all__)
del plugin_getter_

from . import pyfai_integration_base

__all__.extend(pyfai_integration_base.__all__)
del pyfai_integration_base
