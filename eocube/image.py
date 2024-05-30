"""
API - EO Data Cube.

Python Client Library for Earth Observation Data Cubes.
This abstraction uses STAC.py library provided by BDC Project.

=======================================
begin                : 2021-05-01
git sha              : $Format:%H$
copyright            : (C) 2024 by none
email                : baggio.silva@inpe.br
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
import dask.array as da
import rasterio
from dask.base import tokenize
from rasterio.windows import Window



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
        try:
            self.time = datetime.datetime.strptime(
                item.properties['datetime'],
                  '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            self.time = datetime.datetime.strptime(
                item.properties['datetime'],
                  '%Y-%m-%dT%H:%M:%S')
        
        self.item = item
        self.bands = bands
        self.bbox = bbox
        self.tile = item.properties['bdc:tiles'][0]

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

        if self.bbox:
                # Check Authorization
            _ = Utils.safe_request(self.item.assets[band_name].href, method='head')

            source_crs = 4326
            if crs:
                source_crs = CRS.from_string(crs)

            with rasterio.open(self.item.assets[band_name].href) as dataset:
                new_bbox = Utils.reproj_bbox(self.bbox,source_crs)
                window = from_bounds(*new_bbox, dataset.transform)

                asset = dataset.read(1, window=window)
        else:
            with rasterio.open(self.item.assets[band_name].href) as dataset:
                asset = dataset.read(1)

            
    
        return asset
    
    def read_raster(self,band_name, band=None, block_size=1):
        """Read all or some bands from raster

        Arguments:
            path {string} -- path to raster file

        Keyword Arguments:
            band {int, iterable(int)} -- band number or iterable of bands.
                When passing None, it reads all bands (default: {None})
            block_size {int} -- block size multiplier (default: {1})

        Returns:
            dask.array.Array -- a Dask array
        """
        return self.read_raster_band(self.item.assets[band_name].href, band=1, block_size=block_size)
        


    def read_raster_band(self,path, band=1, block_size=1):
        """Read a raster band and return a Dask array

        Arguments:
            path {string} -- path to the raster file

        Keyword Arguments:
            band {int} -- number of band to read (default: {1})
            block_size {int} -- block size multiplier (default: {1})

        """
        def read_window(raster_path, window, band):
            with rasterio.open(raster_path) as src:
                return src.read(band, window=window)

        def resize_window(window, block_size):
            return Window(
                col_off=window.col_off * block_size,
                row_off=window.row_off * block_size,
                width=window.width * block_size,
                height=window.height * block_size)

        def block_windows(dataset, band, block_size):
            return [(pos, resize_window(win, block_size))
                    for pos, win in dataset.block_windows(band)]

        with rasterio.open(path) as src:
            h, w = src.block_shapes[band - 1]
            chunks = (h * block_size, w * block_size)
            name = 'raster-{}'.format(tokenize(path, band, chunks))
            dtype = src.dtypes[band - 1]
            shape = src.height, src.width
            blocks = block_windows(src, band, block_size)

        dsk = {(name, i, j): (read_window, path, window, band)
            for (i, j), window in blocks}

        return da.Array(dsk, name=name, chunks=chunks, dtype=dtype, shape=shape)


    def get_band_count(raster_path):
        """Read raster band count"""
        with rasterio.open(raster_path) as src:
            return src.count
    

    def getWindow(self, band_name,crs=None):
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

        with rasterio.open(self.item.assets[band_name].href) as dataset:
            windows = [window for ij, window in dataset.block_windows()]

            asset = dataset.read(1, window=windows[0])
            
    
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
