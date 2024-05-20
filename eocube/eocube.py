"""
API - EO Data Cube.

Python Client Library for Earth Observation Data Cubes.
This abstraction uses STAC.py library provided by BDC Project.

=======================================
begin                : 2021-05-01
git sha              : $Format:%H$
copyright            : (C) 2020 by none
email                : baggio.silva@inpe.br
=======================================

This program is free software.
You can redistribute it and/or modify it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
"""

import datetime
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pystac_client
import xarray as xr
import logging
from typing import List, Tuple, Dict, Optional
from dask import delayed, compute
from ipywidgets import interact
import re
from dask.distributed import Client


from eocube import config

from .image import Image
from .spectral import Spectral
from .utils import Utils,interpolate_mtx_numba
from .api_check import *

warnings.filterwarnings("ignore")


class DataCube:
    """
    Abstraction to create earth observation data cubes using images collected by STAC.py.
    
    Parameters:
    - collections: List[str] - List of collection names selected by the user.
    - query_bands: List[str] - List of common names of bands (e.g., nir, ndvi, red).
    - bbox: Tuple[float, float, float, float] - Bounding box with the user's Area of Interest.
    - start_date: str - Start date formatted as "yyyy-mm-dd".
    - end_date: str - End date formatted as "yyyy-mm-dd".
    - limit: int - Limit of response images in decreasing order.
    
    Methods:
    - nearTime
    - search
    - getTimeSeries
    - calculateNDVI
    - calculateNDBI
    - calculateNDWI
    - calculateColorComposition
    - classifyDifference
    - interactPlot
    
    Raises:
    - AttributeError: If a parameter is not correctly formatted.
    - ValueError: If the start date is greater than the end date or no data cube is created.
    - RuntimeError: If the STAC service is unreachable due to connection issues.
    """

    def __init__(self, collections: List[str], query_bands: List[str], bbox: Tuple[float, float, float, float], 
                 start_date: str, end_date: str, limit: int = 30):
        check_that(collections, msg="Please insert a list of available collections!")
        check_that(query_bands, msg="Please insert a list of available bands with query_bands!")
        check_that(bbox, msg="Please insert a bounding box parameter!")


        self.utils = Utils()
        self.collections = collections
        self.query_bands = query_bands
        self.bbox = self._validate_bbox(bbox)
        self.start_date, self.end_date = self._validate_dates(start_date, end_date)

        self.utils = Utils()
        self.stac_client = self._initialize_stac_client()
        self.stac_client.add_conforms_to("ITEM_SEARCH")
        self.stac_client.add_conforms_to("QUERY")
        self.timeline = []
        self.data_images = {}
        self.data_array = None

        

        items = self._search_stac(limit)
        images = self._create_images_from_items(items)

        if not images:
            raise ValueError("No data cube created!")

        self.data_images, self.data_array = self._build_data_array(images)
        self.description = self._get_collections_description()

    def _initialize_stac_client(self):
        parameters = dict(access_token=config.ACCESS_TOKEN)
        return pystac_client.Client.open(config.STAC_URL, parameters=parameters)

    def _validate_bbox(self, bbox):
        check_bbox_format(bbox, msg="Invalid bounding box parameter!")
        return bbox

    def _validate_dates(self, start_date: str, end_date: str):
        check_date_range(start_date, end_date)
        return start_date, end_date

    def _search_stac(self, limit: int):
        try:
            item_search = self.stac_client.search(
                collections=self.collections,
                bbox=self.bbox,
                datetime=f'{self.start_date}/{self.end_date}',
                limit=limit
            )

            pattern = re.compile(r"_(\d{6})_\d{8}$")
            items_aux = list(item_search.items())
            unique_numbers = list(np.unique([pattern.findall(item.id)[0] for item in items_aux]))
            return [[item for item in items_aux if re.search(fr"_{tile}_", item.id)] for tile in unique_numbers]
        except Exception as e:
            logging.error("Failed to search STAC service.", exc_info=True)
            raise RuntimeError("Connection refused!") from e

    def _create_images_from_items(self, items):
        images = []
        if items:
            for item in items[0]:
                bands = {}
                available_bands = item.properties.get('eo:bands')
                for band in available_bands:
                    band_name = str(band.get('name'))
                    if band_name in self.query_bands:
                        bands[band_name] = band_name
                images.append(
                    Image(
                        item=item,
                        bands=bands,
                        bbox=self.bbox
                    )
                )
        return images

    def _build_data_array(self, images):
        x_data = {}
        for image in images:
            date = image.time
            self.data_images[date] = image
            x_data[date] = []
            for band in self.query_bands:
                data = delayed(image.getBand)(band)
                x_data[date].append({str(band): data})

        self.timeline = sorted(list(x_data.keys()))

        data_timeline = {}
        for i in range(len(self.query_bands)):
            data_timeline[self.query_bands[i]] = []
            for time in self.timeline:
                data_timeline[self.query_bands[i]].append(x_data[time][i][self.query_bands[i]])

        time_series = []
        for band in self.query_bands:
            time_series.append(data_timeline[band])

        return self.data_images, xr.DataArray(
            np.array(time_series),
            coords=[self.query_bands, self.timeline],
            dims=["band", "time"],
            name="DataCube"
        )

    def _get_collections_description(self):
        description = {}
        for collection in self.collections:
            response = self.stac_client.get_collection(collection)
            description[str(response.id)] = str(response.title)
        return description

    def nearTime(self, time: str):
        _date = self.data_array.sel(time=time, method="nearest").time.values
        _date = datetime.datetime.utcfromtimestamp(_date.tolist() / 1e9)
        return _date

    def search(self, 
           start_date: Optional[str] = None, end_date: Optional[str] = None,
           as_time_series: bool = False,interpolate: bool = False):
        """Search method to retrieve data from delayed dataset and return all dataset for black searches but takes longer.

        Parameters:
        - band <string, optional>: The common name of band (nir, ndvi, red, ... see info.collections).
        - start_date <string, optional>: The string start date formatted "yyyy-mm-dd" to complete the interval.
        - end_date <string, optional>: The string end date formatted "yyyy-mm-dd" to complete the interval and retrieve a dataset.
        - as_time_series <bool, optional>: If True, return the result as a time series.

        Raise:
        - KeyError: If the given parameter does not exist.
        """
        _start_date = self.nearTime(start_date) if start_date else self.nearTime(self.start_date)
        _end_date = self.nearTime(end_date) if end_date else self.nearTime(self.end_date)
        _bands = self.query_bands
        _timeline = self.timeline

        tasks = [self.data_array.loc[band, _start_date:_end_date].values for band in _bands]

        computed_data = compute(*[item for sublist in tasks for item in sublist])
        
        if as_time_series:
            ts_data = np.array([computed_data[i:i+len(_timeline)] for i in range(0, len(computed_data), len(_timeline))])
            result = self.cube_to_time_series(ts_data, _bands, _timeline)
            
        else:
            _data = np.array([computed_data[i:i+len(_timeline)] for i in range(0, len(computed_data), len(_timeline))])
            result = xr.DataArray(
                _data,
                coords={"band": _bands, "time": _timeline, "y": range(_data.shape[2]), "x": range(_data.shape[3])},
                dims=["band", "time", "y", "x"],
                name="DataCube"
            )

        result.attrs['product'] = self.description
        return result

    def cube_to_time_series(self, data_array, bands, time_coords):
        """Transform the data cube into a time series cube."""
        y_dim, x_dim = data_array.shape[2], data_array.shape[3]
        band_ts_list = []

        for i, band in enumerate(bands):
            band_data = data_array[i]
            flattened_data = band_data.reshape(len(time_coords), -1).transpose(1, 0)
            
            ts_data = xr.DataArray(
                flattened_data,
                coords={"pixel": range(flattened_data.shape[0]), "time": time_coords, "band": band},
                dims=["pixel", "time"],
                name="TimeSeries"
            )
            band_ts_list.append(ts_data)
        
        combined_ts_data = xr.concat(band_ts_list, dim="band")
        combined_ts_data.attrs['y_dim'] = y_dim
        combined_ts_data.attrs['x_dim'] = x_dim

        return combined_ts_data
    
    def getTimeSeries(self, band: str, lon: float, lat: float, start_date: Optional[str] = None, end_date: Optional[str] = None):
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

    def classifyDifference(self, band: str, start_date: str, end_date: str, limiar_min: float = 0, limiar_max: float = 0):
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

    def interactPlot(self, method: str):
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
                if method in ['red', 'green', 'blue']:
                    colormap = plt.get_cmap('Greys', 255).reversed()
                plt.imshow(self.data_images[date].getBand(method), cmap=colormap)
                plt.title(f'\nComposição da Banda {method.upper()} {date} \n')
                plt.colorbar()
            else:
                raise ValueError("Please insert a valid method rgb, ndvi, ndwi, ndbi, ... or any of selected bands!")
            plt.tight_layout()
            plt.show()
