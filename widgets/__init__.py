#!/usr/bin/env python

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

"""Package with modified widgets required for creating the graphical user
interface"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []


from . import dialogues

from . import plugin_config

from . import confirmation_bar
from .confirmation_bar import *

from . import plugin_collection_presenter
from .plugin_collection_presenter import *

from . import scroll_area
from .scroll_area import *

from . import utilities
from .utilities import *

from . import workflow_plugin
from .workflow_plugin import *

from . import workflow_tree_canvas
from .workflow_tree_canvas import *

from . import central_widget_proxy
from .central_widget_proxy import *

__all__ += confirmation_bar.__all__
__all__ += plugin_collection_presenter.__all__
__all__ += scroll_area.__all__
__all__ += utilities.__all__
__all__ += workflow_plugin.__all__
__all__ += workflow_tree_canvas.__all__
__all__ += central_widget_proxy.__all__

# unclutter namespace and remove modules:
del confirmation_bar
del plugin_collection_presenter
del scroll_area
del utilities
del workflow_plugin
del workflow_tree_canvas
del central_widget_proxy