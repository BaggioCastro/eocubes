"""
API - EO Data Cube.

Python Client Library for Earth Observation Data Cubes.
This abstraction uses STAC.py library provided by BDC Project.

=======================================
begin                : 2021-05-01
git sha              : $Format:%H$
copyright            : (C) 2020 by none
email                : none@inpe.br
=======================================

This program is free software.
You can redistribute it and/or modify it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
"""


import datetime

from .spectral import Spectral
from .utils import Utils

import rasterio
from rasterio.crs import CRS
from rasterio.warp import transform
from rasterio.windows import from_bounds


class Image():
    """Abstraction to rasters files collected by STAC.py.

    Parameters

     - item <ItemCollection, required>: The ItemCollection from STAC Python Library. GeoJSON Feature Collection of STAC Items.

     - bands <dictionary, required>: A python dictionary with bands real name referenced by key with commom name.

     - bbox <tupple, required>: The bounding box value with longitude and latitude values.

    Methods:

        listBands, getBand,
        getNDVI, getNDWI, getNDBI, getRGB,
        _afimPointsToCoord, _afimCoordsToPoint

    Raise

     - AttributeError and ValueError: If a given parameter is not correctly formatted.
    """

    def __init__(self, item, bands, bbox):
        """Build the Image Object for collected items from STAC."""
        self.utils = Utils()
        self.spectral = Spectral()
        self.time = datetime.datetime.strptime(
            item.properties['datetime'],
            '%Y-%m-%dT%H:%M:%S'
        )
        self.item = item
        self.bands = bands
        self.bbox = bbox

    def listBands(self):
        """Get a list with available bands commom name."""
        return list(self.bands.keys())

    def getBand(self, band_name,crs=None):
        from rasterio.windows import from_bounds
        """Get bands from STAC item using commom name for band.

        Parameters

         - band <string, required>: The band commom name.

         - wd <rasterio.Window, optional>: The window from rasterio abstration for crop images.

        Raise

         - ValueError: If the resquested key not exists.

        """
            # Check Authorization
        _ = Utils.safe_request(self.item.assets[band_name].href, method='head')

        source_crs = 4326
        if crs:
            source_crs = CRS.from_string(crs)

        with rasterio.open(self.item.assets[band_name].href) as dataset:
            if self.bbox:
                new_bbox = Utils.reproj_bbox(self.bbox,source_crs)
                window = from_bounds(*new_bbox, dataset.transform)

            asset = dataset.read(1, window=window)
            
    
        return asset
    
    

    def getNDVI(self):
        """Calculate the Normalized Difference Vegetation Index - NDVI by image colected values.

        Raise

         - KeyError: If the required band does not exist.
        """
        return self.spectral._ndvi(
            nir=self.getBand("B08"),
            red=self.getBand("B04")
        )

    def getNDWI(self):
        """Calculate the Normalized Difference Water Index - NDWI by image colected values.

        Raise

         - KeyError: If the required band does not exist.
        """
        return self.spectral._ndwi(
            nir=self.getBand("B08"),
            green=self.getBand("B03")
        )

    def getNDBI(self):
        """Calculate the Normalized Difference Built-up Index - NDBI by image colected values.

        Raise

         - KeyError: If the required band does not exist.
        """
        return self.spectral._ndbi(
            nir=self.getBand("B08"),
            swir1=self.getBand("B11")
        )

    def getRGB(self):
        """Get thee RGB image with real color.

        Raise

         - KeyError: If the required band does not exist.
        """
        return self.spectral._rgb(
            red=self.getBand("B04"),
            green=self.getBand("B03"),
            blue=self.getBand("B02")
        )

    def _afimPointsToCoord(self, x, y, band):
        """Calculate the long lat of a given point from band matrix.

        Parameters

         - x <int, required>: For colunms.

         - y <int, required>: For lines.

         - band <string, required>: An available band to create a dataset.

        Raise

         - ValueError: If the resquested coordinate is invalid or not typed.
        """
        link = self.item.assets[
            self.bands[band]
        ]['href']
        point0 = self.utils._afimCoordsToPoint(link, self.bbox[0], self.bbox[1])
        pointX = (point0[0] + x, point0[1] + y)
        coordX = self.utils._afimPointsToCoord(link, pointX[0], pointX[1])
        return coordX

    def _afimCoordsToPoint(self, lon, lat, band):
        """Calculate the x y of a given point lon lat from band matrix.

        Parameters

         - lon <float, required>: For longitude EPSG:4326.

         - lat <float, required>: For latitude EPSG:4326.

         - band <string, required>: An available band to create a dataset.

        Raise

         - ValueError: If the resquested coordinate is invalid or not typed.
        """
        link = self.item.assets[
            self.bands[band]
        ]['href']
        coord0 = self._afimPointsToCoord(0, 0, band)
        point0 = self.utils._afimCoordsToPoint(link, coord0[0], coord0[1])
        pointX = self.utils._afimCoordsToPoint(link, lon, lat)
        result = (
            abs(point0[0] - pointX[0]),
            abs(point0[1] - pointX[1])
        )
        return result
