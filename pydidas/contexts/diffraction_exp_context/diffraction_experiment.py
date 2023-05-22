# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
Module with the DiffractionExperiment class which is used to manage global information
about the experiment independant from the individual frames.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DiffractionExperiment"]


import numpy as np
import pyFAI
from qtpy import QtCore

from ...core import (
    ObjectWithParameterCollection,
    UserConfigError,
    get_generic_param_collection,
)
from ...core.constants import LAMBDA_IN_A_TO_E, PYFAI_DETECTOR_NAMES
from ...core.utils import NoPrint, SignalBlocker
from .diffraction_experiment_io import DiffractionExperimentIo


class DiffractionExperiment(ObjectWithParameterCollection):
    """
    Class which holds experimental settings for diffraction experiments.

    This class must be used with care. Usually, the unique DiffractionExperimentContext
    should be used to access the active instance.

    The singleton factory will allow access to the single instance through
    :py:class:`
    pydidas.contexts.diffraction_exp_context.DiffractionExperimentContext`.
    """

    default_params = get_generic_param_collection(
        "xray_wavelength",
        "xray_energy",
        "detector_name",
        "detector_npixx",
        "detector_npixy",
        "detector_pxsizex",
        "detector_pxsizey",
        "detector_mask_file",
        "detector_dist",
        "detector_poni1",
        "detector_poni2",
        "detector_rot1",
        "detector_rot2",
        "detector_rot3",
    )
    sig_params_changed = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        ObjectWithParameterCollection.__init__(self)
        self.add_params(*args)
        self.set_default_params()
        self.update_param_values_from_kwargs(**kwargs)

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
        if param_key == "xray_energy":
            self.params["xray_energy"].value = value
            self.params["xray_wavelength"].value = LAMBDA_IN_A_TO_E / value
        elif param_key == "xray_wavelength":
            self.params["xray_wavelength"].value = value
            self.params["xray_energy"].value = LAMBDA_IN_A_TO_E / value
        else:
            self.params.set_value(param_key, value)
        self.sig_params_changed.emit()

    def get_detector(self):
        """
        Get the pyFAI detector object.

        If a pyFAI detector can be instantiated from the "detector" Parameter
        value, this object will be used. Otherwise, a new detector is created
        and values from the DiffractionExperimentContext are copied.

        Returns
        -------
        det : pyFAI.detectors.Detector
            The detector object.
        """
        _name = self.get_param_value("detector_name")
        if _name in PYFAI_DETECTOR_NAMES:
            _det = pyFAI.detector_factory(_name)
        else:
            _det = pyFAI.detectors.Detector()
        for key, value in [
            ["pixel1", self.get_param_value("detector_pxsizey") * 1e-6],
            ["pixel2", self.get_param_value("detector_pxsizex") * 1e-6],
            [
                "max_shape",
                (
                    self.get_param_value("detector_npixy"),
                    self.get_param_value("detector_npixx"),
                ),
            ],
        ]:
            setattr(_det, key, value)
        return _det

    def as_pyfai_geometry(self):
        """
        Get an equivalent pyFAI Geometry object.

        Returns
        -------
        pyFAI.geometry.Geometry :
            The pyFAI geometry object corresponding to the DiffractionExperiment config.
        """
        return pyFAI.geometry.Geometry(
            dist=self.get_param_value("detector_dist"),
            poni1=self.get_param_value("detector_poni1"),
            poni2=self.get_param_value("detector_poni2"),
            rot1=self.get_param_value("detector_rot1"),
            rot2=self.get_param_value("detector_rot2"),
            rot3=self.get_param_value("detector_rot3"),
            detector=self.get_detector(),
        )

    def set_detector_params_from_name(self, det_name):
        """
        Set the detector parameters based on a detector name.

        This method will query the pyFAI library for the detector parameters
        and update the internal Parameters.

        Parameters
        ----------
        det_name : str
            The pyFAI name for the detector.

        Raises
        ------
        NameError
            If the specified detector name is unknown by pyFAI.
        """
        if det_name in PYFAI_DETECTOR_NAMES:
            _det = pyFAI.detector_factory(det_name)
        else:
            raise UserConfigError(
                f"The detector name '{det_name}' is unknown to pyFAI."
            )
        with SignalBlocker(self):
            self.set_param_value("detector_pxsizey", _det.pixel1 * 1e6)
            self.set_param_value("detector_pxsizex", _det.pixel2 * 1e6)
            self.set_param_value("detector_npixy", _det.max_shape[0])
            self.set_param_value("detector_npixx", _det.max_shape[1])
            self.set_param_value("detector_name", _det.name)
        self.sig_params_changed.emit()

    def update_from_diffraction_exp(self, diffraction_exp):
        """
        Update this DiffractionExperiment object's Parameters from another instance.

        The purpose of this method is to "copy" the other DiffractionExperiment's
        Parameter values while keeping the reference to this object.

        Parameters
        ----------
        diffraction_exp : DiffractionExperiment
            The other DiffractionExperiment from which the Parameters should be taken.
        """
        with SignalBlocker(self):
            for _key, _val in diffraction_exp.get_param_values_as_dict().items():
                self.set_param_value(_key, _val)
        self.sig_params_changed.emit()

    def update_from_pyfai_geometry(self, geometry):
        """
        Update this DiffractionExperiment from a pyFAI geometry.

        Parameters
        ----------
        geometry : pyFAI.geometry.Geometry
            The geometry to be used.
        """
        with SignalBlocker(self):
            for _key in ["dist", "poni1", "poni2", "rot1", "rot2", "rot3"]:
                self.set_param_value(f"detector_{_key}", getattr(geometry, _key))
            if geometry.detector.name in pyFAI.detectors.Detector.registry:
                self.set_detector_params_from_name(geometry.detector.name)
            else:
                _det = geometry.detector
                if _det.pixel1 is not None:
                    self.set_param_value("detector_pxsizey", _det.pixel1 * 1e6)
                if _det.pixel2 is not None:
                    self.set_param_value("detector_pxsizex", _det.pixel2 * 1e6)
                if _det.max_shape is not None:
                    self.set_param_value("detector_npixy", _det.max_shape[0])
                    self.set_param_value("detector_npixx", _det.max_shape[1])
                if [_det.pixel1, _det.pixel2, _det.max_shape] != [None, None, None]:
                    self.set_param_value("detector_name", _det.name)
        self.sig_params_changed.emit()

    def import_from_file(self, filename):
        """
        Import DiffractionExperimentContext from a file.

        Parameters
        ----------
        filename : Union[str, pathlib.Path]
            The full filename.
        """
        with SignalBlocker(self):
            DiffractionExperimentIo.import_from_file(filename, diffraction_exp=self)
        self.sig_params_changed.emit()

    def export_to_file(self, filename, overwrite=False):
        """
        Import DiffractionExperimentContext from a file.

        Parameters
        ----------
        filename : Union[str, pathlib.Path]
            The full filename.
        overwrite : bool, optional
            Keyword to allow overwriting of existing files.
        """
        DiffractionExperimentIo.export_to_file(
            filename, diffraction_exp=self, overwrite=overwrite
        )

    def set_beamcenter_from_fit2d_params(self, center_x, center_y, det_dist, **kwargs):
        """
        Set the beamcenter in detector pixel coordinates.

        The center_x and center_y parameters define the position of the beam center on
        the detector. The optional rot_x, rot_y and rot_beam allow to add a rotation
        around axes parallel to the detector x and y direction and around the beam.
        Following the pyFAI geometry, the order of rotations is:

        R_pyfai = R_3(rot_beam) * R_2(-rot_x) * R_1(-rot_y)

        Note that rot_x and rot_y directors are lefthanded (i.e. inverted.)

        Parameters
        ----------
        center_x : float
            The position of the x beam center in pixels.
        center_y : float
            The position of the y beam center in pixels.
        det_dist : float
            The distance between sample and detector beam center in meters.
        tilt : float, optional
            The tilt of the detector, given in rotation unit. The default is 0.
        tilt_plane: float, optional
            The rotation of the tile plane of the detector, given in rot unit. The
            default is 0.
        rot_unit : str, optional
            The unit of the rotation angles. Allowed choices are 'degree' and 'rad'.
            The default is degree.
        """
        _tilt = kwargs.get("tilt", 0)
        _tilt_plane = kwargs.get("tilt_plane", 0)
        if kwargs.get("rot_unit", "degree") == "rad":
            _tilt = _tilt * 180 / np.pi
            _tilt_plane = _tilt_plane * 180 / np.pi
        with NoPrint():
            _geo = pyFAI.geometry.fit2d.convert_from_Fit2d(
                dict(
                    directDist=det_dist * 1e3,
                    centerX=center_x,
                    centerY=center_y,
                    tilt=_tilt,
                    tiltPlanRotation=_tilt_plane,
                    detector=self.get_detector(),
                )
            )
        with SignalBlocker(self):
            for _key in ["dist", "poni1", "poni2", "rot1", "rot2", "rot3"]:
                self.set_param_value(f"detector_{_key}", getattr(_geo, _key))
        self.sig_params_changed.emit()

    @property
    def beamcenter(self):
        """
        Get the beamcenter in detector pixel coordinates.

        Returns
        -------
        center_x : float
            The beamcenter x coordinate (in pixels).
        center_y : float
            The beamcenter y coordinate (in pixels).
        """
        _f2d = self.as_fit2d_geometry_values()
        return _f2d["center_x"], _f2d["center_y"]

    def as_fit2d_geometry_values(self):
        """
        Get the DiffractionExperiment configuration as values in Fit2D geometry.

        Returns
        -------
        dict :
            The geometry in Fit2D nomenclature with center_x, center_y, det_dist,
            tilt and tilt_plane keys.
        """
        if (
            self.get_param_value("detector_pxsizex") == 0
            or self.get_param_value("detector_pxsizey") == 0
        ):
            raise UserConfigError(
                "The detector pixelsize of 0 is invalid for a fit2d geometry."
            )
        _geo = self.as_pyfai_geometry()
        _f2d_geo = pyFAI.geometry.fit2d.convert_to_Fit2d(_geo)
        return {
            "center_x": _f2d_geo.centerX,
            "center_y": _f2d_geo.centerY,
            "det_dist": _f2d_geo.directDist,
            "tilt": _f2d_geo.tilt,
            "tilt_plane": _f2d_geo.tiltPlanRotation,
        }
