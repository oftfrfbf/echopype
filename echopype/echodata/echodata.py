import os
import warnings
import uuid
from collections import OrderedDict
from datetime import datetime as dt
from html import escape
from pathlib import Path

import fsspec
from fsspec.implementations.local import LocalFileSystem

import xarray as xr
import zarr
from zarr.errors import GroupNotFoundError

from ..utils.repr import HtmlTemplate
from ..utils import io
from .convention import _get_convention

XARRAY_ENGINE_MAP = {
    ".nc": "netcdf4",
    ".zarr": "zarr",
}


class EchoData:
    """Echo data model class for handling raw converted data,
    including multiple files associated with the same data set.
    """

    def __init__(
            self,
            converted_raw_path=None,
            storage_options=None,
    ):

        # TODO: consider if should open datasets in init
        #  or within each function call when echodata is used. Need to benchmark.

        self.converted_raw_path = converted_raw_path
        self.storage_options = storage_options if storage_options is not None else {}

        self.__setup_groups()
        if converted_raw_path:
            # TODO: verify if converted_raw_path is valid on either local or remote filesystem
            self._load_file(converted_raw_path)
            self.sonar_model = self.top.keywords

    def __repr__(self) -> str:
        """Make string representation of InferenceData object."""
        existing_groups = [
            f"{self.__group_map[group]['name']}: {self.__group_map[group]['description']}"  # noqa
            for group in self.__group_map.keys()
            if isinstance(getattr(self, group), xr.Dataset)
        ]
        msg = "EchoData: standardized raw data from {file_path}\n  > {options}".format(
            options="\n  > ".join(existing_groups),
            file_path=self.converted_raw_path,
        )
        return msg

    def _repr_html_(self) -> str:
        """Make html representation of InferenceData object."""
        try:
            from xarray.core.options import OPTIONS

            display_style = OPTIONS["display_style"]
            if display_style == "text":
                html_repr = f"<pre>{escape(repr(self))}</pre>"
            else:
                xr_collections = []
                for group in self.__group_map.keys():
                    if isinstance(getattr(self, group), xr.Dataset):
                        xr_data = getattr(self, group)._repr_html_()
                        xr_collections.append(
                            HtmlTemplate.element_template.format(  # noqa
                                group_id=group + str(uuid.uuid4()),
                                group_name=self.__group_map[group]["name"],
                                group_description=self.__group_map[group]["description"],
                                xr_data=xr_data,
                            )
                        )
                elements = "".join(xr_collections)
                formatted_html_template = HtmlTemplate.html_template.format(
                    elements, file_path=str(self.converted_raw_path)
                )  # noqa
                css_template = HtmlTemplate.css_template  # noqa
                html_repr = "%(formatted_html_template)s%(css_template)s" % locals()
        except:  # noqa
            html_repr = f"<pre>{escape(repr(self))}</pre>"
        return html_repr

    def __setup_groups(self):
        self.__group_map = OrderedDict(_get_convention()["groups"])
        for group in self.__group_map.keys():
            setattr(self, group, None)

    @classmethod
    def _load_convert(cls, convert_obj):
        new_cls = cls()
        for group in new_cls.__group_map.keys():
            if hasattr(convert_obj, group):
                setattr(new_cls, group, getattr(convert_obj, group))

        setattr(new_cls, "sonar_model", getattr(convert_obj, "sonar_model"))
        setattr(new_cls, "source_file", getattr(convert_obj, "source_file"))
        return new_cls

    def _load_file(self, raw_path):
        """Lazy load Top-level, Beam, Environment, and Vendor groups from raw file."""
        for group, value in self.__group_map.items():
            # EK80 data may have a Beam_power group if both complex and power data exist.
            try:
                ds = self._load_group(raw_path, group=value["ep_group"])
            except (OSError, GroupNotFoundError):
                if group == "beam_power":
                    ds = None
                    pass
            if group == "top":
                self.sonar_model = ds.keywords.upper()

            if isinstance(ds, xr.Dataset):
                setattr(self, group, ds)

    def _check_path(self):
        """ Check if converted_raw_path exists """
        pass

    @staticmethod
    def _load_group(filepath, group=None):
        # TODO: handle multiple files through the same set of checks for combining files
        suffix = Path(filepath).suffix
        if suffix not in XARRAY_ENGINE_MAP:
            raise ValueError("Input file type not supported!")

        return xr.open_dataset(filepath, group=group, engine=XARRAY_ENGINE_MAP[suffix])

    def to_netcdf(self, **kwargs):
        """Save content of EchoData to netCDF.

        Parameters
        ----------
        save_path : str
            path that converted .nc file will be saved
        compress : bool
            whether or not to perform compression on data variables
            Defaults to ``True``
        overwrite : bool
            whether or not to overwrite existing files
            Defaults to ``False``
        parallel : bool
            whether or not to use parallel processing. (Not yet implemented)
        output_storage_options : dict
            Additional keywords to pass to the filesystem class.
        """
        from .api import to_file

        return to_file(self, "netcdf4", **kwargs)

    def to_zarr(self, **kwargs):
        """Save content of EchoData to zarr.

        Parameters
        ----------
        save_path : str
            path that converted .nc file will be saved
        compress : bool
            whether or not to perform compression on data variables
            Defaults to ``True``
        overwrite : bool
            whether or not to overwrite existing files
            Defaults to ``False``
        parallel : bool
            whether or not to use parallel processing. (Not yet implemented)
        output_storage_options : dict
            Additional keywords to pass to the filesystem class.
        """
        from .api import to_file

        return to_file(self, "zarr", **kwargs)
