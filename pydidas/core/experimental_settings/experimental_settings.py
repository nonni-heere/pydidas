# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Module with the GlobalSettings class which is used to manage global
information independant from the individual frames."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ExperimentalSettings']


import pyFAI

from ...constants import LAMBDA_TO_E
from ..singleton_factory import SingletonFactory
from ..parameter_collection import ParameterCollection
from ..generic_parameters import get_generic_parameter
from ..object_with_parameter_collection import ObjectWithParameterCollection
from .experimental_settings_io_meta import ExperimentalSettingsIoMeta

DEFAULTS = ParameterCollection(
    get_generic_parameter('xray_wavelength'),
    get_generic_parameter('xray_energy'),
    get_generic_parameter('detector_name'),
    get_generic_parameter('detector_npixx'),
    get_generic_parameter('detector_npixy'),
    get_generic_parameter('detector_sizex'),
    get_generic_parameter('detector_sizey'),
    get_generic_parameter('detector_dist'),
    get_generic_parameter('detector_poni1'),
    get_generic_parameter('detector_poni2'),
    get_generic_parameter('detector_rot1'),
    get_generic_parameter('detector_rot2'),
    get_generic_parameter('detector_rot3'))


class _ExpSettings(ObjectWithParameterCollection):
    """
    Inherits from :py:class:`pydidas.core.ObjectWithParameterCollection
    <pydidas.core.ObjectWithParameterCollection>`

    Class which holds experimental settings. This class must only be
    instanciated through its factory, therefore guaranteeing that only a
    single instance exists.

    The factory will allow access to the single instance through
    :py:class:`pydidas.core.experimental_settings.ExperimentalSettings`.
    """
    default_params = DEFAULTS

    def __init__(self, *args, **kwargs):
        """Setup method"""
        ObjectWithParameterCollection.__init__(self)
        self.add_params(*args, **kwargs)
        self.set_default_params()

    def set_param_value(self, param_key, value):
        """
        Set a Parameter value.

        This method overloads the inherited set_param_value method to update
        the linked parameters of X-ray energy and wavelength.

        Parameters
        ----------
        key : str
            The Parameter identifier key.
        value : object
            The new value for the parameter. Depending upon the parameter,
            value can take any form (number, string, object, ...).

        Raises
        ------
        KeyError
            If the key does not exist.
        """
        self._check_key(param_key)
        if param_key == 'xray_energy':
            self.params['xray_wavelength'].value = (
                LAMBDA_TO_E / (value * 1e-10))
            self.params['xray_energy'].value = value
        elif param_key == 'xray_wavelength':
            self.params['xray_wavelength'].value = value
            self.params['xray_energy'].value = LAMBDA_TO_E / (value * 1e-10)
        else:
            self.params.set_value(param_key, value)

    def get_detector(self):
        """
        Get the detector. First, it is checked whether a pyFAI detector can
        be instantiated from the Detector name or a new detector is created
        and values from the ExperimentalSettings are copied.

        Returns
        -------
        _det : pyFAI.detectors.Detector
            The detector object.
        """
        _name = self.get_param_value('detector_name')
        try:
            _det = pyFAI.detector_factory(_name)
        except RuntimeError:
            _det = pyFAI.detectors.Detector()
        for key, value in [
                ['pixel1', self.get_param_value('detector_sizey')],
                ['pixel2', self.get_param_value('detector_sizex')],
                ['max_shape', (self.get_param_value('detector_npixy'),
                               self.get_param_value('detector_npixx'))]
                ]:
            if getattr(_det, key) != value:
                setattr(_det, key, value)
        return _det

    @staticmethod
    def import_from_file(filename):
        """
        Import ExperimentalSettings from a file.

        Parameters
        ----------
        filename : Union[str, pathlib.Path]
            The full filename.
        """
        ExperimentalSettingsIoMeta.import_from_file(filename)

    @staticmethod
    def export_to_file(filename):
        """
        Import ExperimentalSettings from a file.

        Parameters
        ----------
        filename : Union[str, pathlib.Path]
            The full filename.
        """
        ExperimentalSettingsIoMeta.export_to_file(filename)

    def __copy__(self):
        """
        Overload copy to return self.
        """
        return self


ExperimentalSettings = SingletonFactory(_ExpSettings)
