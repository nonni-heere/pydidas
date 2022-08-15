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
Module with the PyFAI2dIntegration Plugin which allows to integrate diffraction
patterns into a 2D radial/azimuthal map.

"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PyFAI2dIntegration"]

from pydidas.core import Dataset
from pydidas.plugins import pyFAIintegrationBase

import numpy as np


class PyFAI2dIntegration(pyFAIintegrationBase):
    """
    Integrate an image in 2D using pyFAI.

    For a full documentation of the Plugin, please refer to the pyFAI
    documentation.
    """

    plugin_name = "pyFAI 2D integration"
    basic_plugin = False
    input_data_dim = 2
    output_data_dim = 2
    output_data_label = "Integrated data"
    output_data_unit = "a.u."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mask = None
        self._maskval = None
        self.set_param_value("rad_npoint", 1000)
        self.set_param_value("azi_npoint", 36)

    def execute(self, data, **kwargs):
        """
        Apply a mask to an image (2d data-array).

        Parameters
        ----------
        data : Union[pydidas.core.Dataset, np.ndarray]
            The image / frame data .
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        _data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        _newdata = self._ai.integrate2d(
            data,
            self.get_param_value("rad_npoint"),
            npt_azim=self.get_param_value("azi_npoint"),
            polarization_factor=1,
            mask=self._mask,
            unit=self.get_pyFAI_unit_from_param("rad_unit"),
            radial_range=self.get_radial_range(),
            azimuth_range=self.get_azimuthal_range_in_deg(),
            method=self._config["method"],
        )
        _range_fact =  np.pi / 180 if "rad" in self.get_param_value("azi_unit") else 1
        _x_label, _x_unit = self.get_param_value("rad_unit").replace(" ", "").split("/")
        _y_label, _y_unit = self.get_param_value("azi_unit").replace(" ", "").split("/")
        _dataset = Dataset(
            _newdata[0],
            axis_labels=[_y_label, _x_label],
            axis_units=[_y_unit, _x_unit],
            axis_ranges=[_newdata[2] * _range_fact, _newdata[1]],
            data_label="integrated intensity",
            data_unit="counts",
        )
        return _dataset, kwargs

    def calculate_result_shape(self):
        """
        Get the shape of the integrated dataset to set up the CRS / LUT.

        Returns
        -------
        tuple
            The new shape: A tuple of two integers is returned.
        """
        self._config["result_shape"] = (
            self.get_param_value("rad_npoint"),
            self.get_param_value("azi_npoint"),
        )
