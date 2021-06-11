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
import json
import warnings

import matplotlib.pyplot as plt
import numpy as np
import requests
import stac
import wtss
import xarray as xr
from dask import delayed
from ipywidgets import interact

from eocube import config

from .image import Image
from .spectral import Spectral
from .utils import Utils

warnings.filterwarnings("ignore")


class DataCube():
    """Abstraction to create earth observation data cubes using images collected by STAC.py.
    Create a data cube using images collected from STAC using Image abstration.

    Parameters

     - collections <list of strings, required>: The list with name of collections selected by user.

     - query_bands <list of strings, required>: The list with commom name of bands (nir, ndvi, red, ... see info.collections).

     - bbox <tupple, required>: The bounding box with user Area of Interest.

     - start_date <string, required>: The string start date formated "yyyy-mm-dd" to complete the interval.

     - end_date <string, required>: The string end date formated "yyyy-mm-dd" to complete the interval.

     - limit <int, required>: The limit of response images in decreasing order.

    Methods:

        nearTime, search, getTimeSeries,
        calculateNDVI, calculateNDBI, calculateNDWI, calculateColorComposition,
        classifyDifference, interactPlot.

    Raise

     - AttributeError and ValueError: If a given parameter is not correctly formatted.

     - RuntimeError: If the STAC service is unreachable caused by connection lost of client or service.
    """

    def __init__(self, collections=[], query_bands=[], bbox=(), start_date=None, end_date=None, limit=30):
        """Build DataCube object with config parameters including access token, STAC url and earth observation service url."""

        if len(config.ACCESS_TOKEN) == 0:
            config.ACCESS_TOKEN = input("Please insert a valid user token from BDC Auth: ")

        if len(config.EOCUBE_URL) == 0:
            config.EOCUBE_URL = input("Please insert a valid url for EO Service: ")

        if len(config.STAC_URL) == 0:
            config.STAC_URL = input("Please insert a valid url for STAC Service: ")

        self.utils = Utils()

        self.stac_client = stac.STAC(
            config.STAC_URL,
            access_token=config.ACCESS_TOKEN
        )

        if not collections:
            raise AttributeError("Please insert a list of available collections!")
        else:
            self.collections = collections

        if not query_bands:
            raise AttributeError("Please insert a list of available bands with query_bands!")
        else:
            self.query_bands = query_bands

        if not bbox:
            raise AttributeError("Please insert a bounding box parameter!")
        else:
            valid = self.utils._validateBBOX(bbox)
            if valid:
                self.bbox = bbox

        try:
            _start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            _end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            if _end_date <= _start_date:
                raise ValueError("Start date is greater than end date!")
            else:
                self.start_date = start_date
                self.end_date = end_date
        except:
            raise AttributeError("Dates are not correctly formatted, should be %Y-%m-%d")

        self.timeline = []
        self.data_images = {}
        self.data_array = None

        items = None
        try:
            # arazenar a query globalmente para utilizar os parametros de bounding box
            # e data inicial e final
            items = self.stac_client.search({
                'collections': self.collections,
                'bbox': self.bbox,
                'datetime': f'{self.start_date}/{self.end_date}',
                'limit': limit
            })
        except:
            raise RuntimeError("Connection refused!")

        images = []
        if items:
            # Cria uma lista de objetos Images com os items no STAC
            for item in items.features:
                bands = {}
                available_bands = item.get('properties').get('eo:bands')
                for band in available_bands:
                    band_common_name = str(band.get('common_name', ''))
                    band_name = str(band.get('name'))
                    # Cria um dicionário com cada chave sendo o nome comum da banda e o nome dado pelo item
                    if band_common_name in self.query_bands:
                        bands[band_common_name] = band.get('name')
                    elif band_name in self.query_bands:
                        bands[band_name] = band_name
                images.append(
                    Image(
                        item=item,
                        bands=bands,
                        bbox=self.bbox
                    )
                )

        # Verifica se o cubo de dados foi criado com sucesso
        if len(images) == 0:
            raise ValueError("No data cube created!")

        x_data = {}
        for image in images:
            date = image.time
            self.data_images[date] = image
            x_data[date] = []
            for band in self.query_bands:
                data = delayed(image.getBand)(band)
                x_data[date].append({
                    str(band): data
                })

        self.timeline = sorted(list(x_data.keys()))

        data_timeline = {}
        for i in range(len(list(self.query_bands))):
            data_timeline[self.query_bands[i]] = []
            for time in self.timeline:
                data_timeline[self.query_bands[i]].append(
                    x_data[time][i][self.query_bands[i]]
                )

        time_series = []
        for band in self.query_bands:
            time_series.append(
                data_timeline[band]
            )

        self.description = {}
        for collection in self.collections:
            response = self.stac_client.collections[collection]
            self.description[str(response["id"])] = str(response["title"])

        self.data_array = xr.DataArray(
            np.array(time_series),
            coords=[self.query_bands, self.timeline], #, y, x],
            dims=["band", "time"], #, "y", "x"],
            name=["DataCube"]
        )
        self.data_array.attrs = self.description

    def nearTime(self, time):
        """Search in all dataset a date time near to given time.
        Return a date time from dataset timeline.

        Parameters

         - time <datetime, required>: the given date time to search formated "yyyy-mm-dd".

        Raise

         - ValueError: If time is not correctly formatted.
        """
        _date = self.data_array.sel(time = time, method="nearest").time.values
        _date = datetime.datetime.utcfromtimestamp(_date.tolist()/1e9)
        return _date

    def search(self, band=None, time=None, start_date=None, end_date=None):
        """Search method to retrieve data from delayed dataset and return all dataset for black searchs but takes longer.

        Parameters:

         - band <string, optional>: The commom name of band (nir, ndvi, red, ... see info.collections).

         - time <string, optional>: The given time to retrieve a sigle image formated "yyyy-mm-dd".

         - start_date <string, optional>: The string start date formated "yyyy-mm-dd" to complete the interval.

         - end_date <string, optional>: The string end date formated "yyyy-mm-dd" to complete the interval and retrieve a dataset.

        Raise:

         - KeyError: If the given parameter not exists.
        """
        result = None
        if start_date and end_date:
            _start_date = self.nearTime(start_date)
            _end_date = self.nearTime(end_date)
        else:
            _start_date = self.nearTime(self.start_date)
            _end_date = self.nearTime(self.end_date)
        if band:
            if time:
                _date = self.nearTime(time)
                _timeline = [_date]
                _data = self.data_array.loc[band, _date].values.reshape(1)
            else:
                _data = self.data_array.loc[band, _start_date:_end_date]
                _timeline = _data.time.values
                _data = _data.values
            _result = []
            for raster in _data:
                value = raster.compute()
                _result.append(value)
                _x = list(range(0, value.shape[1]))
                _y = list(range(0, value.shape[0]))
            result = xr.DataArray(
                np.array(_result),
                coords=[_timeline, _y, _x],
                dims=["time", "y", "x"],
                name=[f"ResultSearch_{band}"]
            )
        else:
            _bands = self.query_bands
            _timeline = self.timeline
            _data = []
            for band in _bands:
                d = self.data_array.loc[band].values
                _data.append(d)
                _y = list(range(0, d.values.shape[1]))
                _x = list(range(0, d.values.shape[2]))
            result = xr.DataArray(
                np.array(_data),
                coords=[_bands, _timeline,_y, _x],
                dims=["band", "time", "y", "x"],
                name=["DataCube"]
            )
        result.attrs = self.description
        return result

    def getTimeSeries(self, band=None, lon=None, lat=None, start_date=None, end_date=None):
        """Get time series band values from a given point and timeline.

        Parameters:

         - band <string, optional>: The commom name of band (nir, ndvi, red, ... see info.collections).

         - lon <float, optional>: The given longitude of point (EPSG:4326).

         - lat <float, optional>: The given latitude of point (EPSG:4326).

         - start_date <string, optional>: The string start date formated "yyyy-mm-dd" to complete the interval.

         - end_date <string, optional>: The string end date formated "yyyy-mm-dd" to complete the interval and retrieve a dataset.

        Raise:

         - KeyError: If the given parameter not exists.
        """
        _image = None

        if start_date and end_date:
            start = start_date
            end = end_date
        else:
            start = self.start_date
            end = self.end_date

        _start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
        _end_date = datetime.datetime.strptime(end, '%Y-%m-%d')

        for time in self.timeline:
            if time.year == _start_date.year and \
                time.month == _start_date.month:
                _image = self.data_images[time]
                break

        if not _image:
            _image = self.data_images[self.timeline[0]]

        point = _image._afimCoordsToPoint(lon, lat, band)

        _data = self.data_array.loc[band, _start_date:_end_date]

        sample = _data.values[0].compute()

        if point[0] > sample.shape[0] and point[1] > sample.shape[1]:
            raise ValueError(f"Given point is out of bounding box {self.bbox}")

        result = []
        for raster in _data.values:
            result.append(raster.compute()[point[0]][point[1]])

        _result = xr.DataArray(
            np.array(result),
            coords=[_data.time],
            dims=["time"],
            name=[f"TimeSeries_{band.upper()}"]
        )
        _result.attrs = {
            "longitude": lon,
            "latitude": lat
        }
        return _result

    def calculateNDVI(self, time):
        """Calculate the Normalized Difference Vegetation Index - NDVI of a given period.

        Parameters

         - time <string, required>: The given time to retrieve a sigle image formated "yyyy-mm-dd".

        Raise:

         - KeyError: No data for given date time selected.
        """
        _date = self.nearTime(time)
        _data = self.data_images[_date].getNDVI()
        _timeline = [_date]
        _x = list(range(0, _data.shape[1]))
        _y = list(range(0, _data.shape[0]))
        result = xr.DataArray(
            np.array([_data]),
            coords=[_timeline, _y, _x],
            dims=["time", "y", "x"],
            name=["ImageNDVI"]
        )
        result.attrs = self.description
        return result

    def calculateNDWI(self, time):
        """Calculate the Normalized Difference Water Index - NDVI of a given period.

        Parameters

         - time <string, required>: The given time to retrieve a sigle image formated "yyyy-mm-dd".

        Raise:

         - KeyError: No data for given date time selected.
        """
        _date = self.nearTime(time)
        _data = self.data_images[_date].getNDWI()
        _timeline = [_date]
        _x = list(range(0, _data.shape[1]))
        _y = list(range(0, _data.shape[0]))
        result = xr.DataArray(
            np.array([_data]),
            coords=[_timeline, _y, _x],
            dims=["time", "y", "x"],
            name=["ImageNDWI"]
        )
        result.attrs = self.description
        return result

    def calculateNDBI(self, time):
        """Calculate the Normalized Difference Built-up Index - NDVI of a given period.

        Parameters

         - time <string, required>: The given time to retrieve a sigle image formated "yyyy-mm-dd".

        Raise:

         - KeyError: No data for given date time selected.
        """
        _date = self.nearTime(time)
        _data = self.data_images[_date].getNDBI()
        _timeline = [_date]
        _x = list(range(0, _data.shape[1]))
        _y = list(range(0, _data.shape[0]))
        result = xr.DataArray(
            np.array([_data]),
            coords=[_timeline, _y, _x],
            dims=["time", "y", "x"],
            name=["ImageNDBI"]
        )
        result.attrs = self.description
        return result

    def calculateColorComposition(self, time):
        """Calculate the color composition RGB of a given period.

        Parameters

         - time <string, required>: The given time to retrieve a sigle image formated "yyyy-mm-dd".

        Raise:

         - KeyError: No data for given date time selected.
        """
        _date = self.nearTime(time)
        _data = self.data_images[_date].getRGB()
        _timeline = [_date]
        _x = list(range(0, _data.shape[1]))
        _y = list(range(0, _data.shape[0]))
        _rgb = ["red", "green", "blue"]
        result = xr.DataArray(
            np.array([_data]),
            coords=[_timeline, _y, _x, _rgb],
            dims=["time", "y", "x", "rgb"],
            name=["ColorComposition"]
        )
        result.attrs = self.description
        return result

    def classifyDifference(self, band, start_date, end_date, limiar_min=0, limiar_max=0):
        """Classify two different images with start and end date based on limiar mim and max.

        Parameters:

         - band <string, required>: The commom name of band (nir, ndvi, red, ... see info.collections).

         - start_date <string, required>: The string start date formated "yyyy-mm-dd" to complete the interval.

         - end_date <string, required>: The string end date formated "yyyy-mm-dd" to complete the interval and retrieve a dataset.

         - limiar_min <float, required>: The minimum value classified to difference.

         - limiar_max <float, required>: The maximum value classified to difference to complete the interval.

        Raise:

         - KeyError: If the given parameter not exists.
        """
        time_1 = self.nearTime(start_date)
        data_1 = self.data_images[time_1].getBand(band)
        time_2 = self.nearTime(end_date)
        data_2 = self.data_images[time_2].getBand(band)
        spectral = Spectral()
        data_1 = spectral._format(data_1)
        data_2 = spectral._format(data_2)
        _data = None
        if spectral._validate_shape(data_1, data_2):
            diff = spectral._matrix_diff(data_1, data_2)
            _data = spectral._classify_diff(diff, limiar_min=limiar_min, limiar_max=limiar_max)
        else:
            raise ValueError("Time 1 and 2 has different shapes!")
        _timeline = [f"{time_1} - {time_2}"]
        _x = list(range(0, _data.shape[1]))
        _y = list(range(0, _data.shape[0]))
        _result = xr.DataArray(
            np.array([_data]),
            coords=[_timeline, _y, _x],
            dims=["time", "y", "x"],
            name=["ClassifyDifference"]
        )
        return _result

    def interactPlot(self, method):
        """Return all dataset with a interactive plot date time slider.

        Parameters:

         - method <string, required>: The method like rgb, ndvi, ndwi, ndbi, ... or any of selected bands.

        Raise:

         - KeyError: If the given parameter not exists.
        """
        @interact(date=self.timeline)
        def sliderplot(date):
            plt.clf()
            plt.figure(figsize=(25, 8))
            if method == 'rgb':
                plt.imshow(self.data_images[date].getRGB())
                plt.title(f'\nComposição Colorida Verdadeira {date} \n')
            elif method == 'ndvi' and not (method in self.query_bands):
                colormap = plt.get_cmap('Greens', 1000)
                plt.imshow(self.data_images[date].getNDVI(), cmap=colormap)
                plt.title(f'\nNDVI - Normalized Difference Vegetation Index {date} \n')
                plt.colorbar()
            elif method == 'ndwi' and not (method in self.query_bands):
                colormap = plt.get_cmap('Blues', 1000)
                plt.imshow(self.data_images[date].getNDWI(), cmap=colormap)
                plt.title(f'\nNDWI - Normalized Difference Water Index {date} \n')
                plt.colorbar()
            elif method == 'ndbi' and not (method in self.query_bands):
                colormap = plt.get_cmap('Greys', 1000)
                plt.imshow(self.data_images[date].getNDBI(), cmap=colormap)
                plt.title(f'\nNDBI - Normalized Difference Built-up Index {date} \n')
                plt.colorbar()
            elif method in self.query_bands:
                colormap = plt.get_cmap('Greys', 1000)
                plt.imshow(self.data_images[date].getBand(method), cmap=colormap)
                plt.title(f'\nComposição da Banda {method.upper()} {date} \n')
                plt.colorbar()
            else:
                raise ValueError("Please insert a valid method rgb, ndvi, ndwi, ndbi, ... or any of selected bands!")
            plt.tight_layout()
            plt.show()
