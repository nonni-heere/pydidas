from base_plugins import InputPlugin, INPUT_PLUGIN
from plugin_workflow_gui.parameter import Parameter

class HdfLoader(InputPlugin):
    plugin_name = 'HDF loader'
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    parameters = [Parameter('fname', param_type=str, default='', tooltip='The file name.'),
                  Parameter('dset', param_type=str, default='', tooltip='The dataset.'),
                  Parameter('sequence', param_type=str, default='', tooltip='The image sequence.')
                  ]
    input_data = []
    output_data = {0: {'name': 'image', 'dim': 2, 'labels': ['det_y', 'det_x']}}

    def execute(self, i, **kwargs):
        import numpy as np
        print(f'Execute plugin {self.name} with arguments: {i}, {kwargs}')
        return np.arange((i)), {}