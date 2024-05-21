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
from .utils import Utils
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
            items = list(item_search.items())
            pattern = re.compile(r"_(\d{6})_\d{8}$")
            unique_tiles = {pattern.findall(item.id)[0] for item in items}
            return [[item for item in items if tile in item.id] for tile in unique_tiles]
        except Exception as e:
            logging.error("Failed to search STAC service.", exc_info=True)
            raise RuntimeError("Connection refused!") from e


    def _create_images_from_items(self, items):
        images = []
        if items:
            for item in items[0]:
                bands = {band['name']: band['name'] for band in item.properties.get('eo:bands') if band['name'] in self.query_bands}
                images.append(Image(item=item, bands=bands, bbox=self.bbox))
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
           as_time_series: bool = False):
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
    
    def calculate_indices(self, cube, input_bands, formulas):
        """
        Calculates the desired spectral indices from the input data matrix using the given formulas.

        Parameters:
        -----------
        cube : xarray.DataArray
            The input data cube.
        input_bands : list of str
            The list of band names to be used for calculating the indices.
        formulas : list of str
            The list of formulas to be used for calculating the indices.

        Returns:
        --------
        cube : xarray.DataArray
            The updated data cube with the calculated indices.
        """
        if not isinstance(cube, xr.DataArray):
            raise ValueError("cube must be an xarray.DataArray")

        # Check for missing bands and download if necessary
        missing_bands = [band for band in input_bands if band not in cube.coords["band"].values]
        if missing_bands:
            self._download_missing_bands(missing_bands)

        # Calculate band values for the input matrix
        band_values = {band: cube.sel(band=band).values for band in input_bands}

        # Calculate the desired indices using the formulas
        index_values = []
        for formula in formulas:
            try:
                index_value = eval(formula, {}, band_values)
                mask = (-1 <= index_value) & (index_value <= 1)
                index_value = np.where(mask, index_value * 10000, index_value)
            except NameError as e:
                print(f"Error: {e}. Please check the input bands and formulas.")
                return None
            index_values.append(index_value)

        # Combine the results into a final array
        final_result = np.stack(index_values, axis=0).astype('int16')

        # Create a new DataArray for the indices
        if "pixel" in cube.coords:
            indices_data_array = xr.DataArray(
                final_result,
                coords={"band": [f"index_{i}" for i in range(len(formulas))], "time": cube.coords["time"], "pixel": cube.coords["pixel"]},
                dims=["band", "time", "pixel"],
                name="SpectralIndices"
            )
        else:
            indices_data_array = xr.DataArray(
                final_result,
                coords={"band": [f"index_{i}" for i in range(len(formulas))], "time": cube.coords["time"], "y": cube.coords["y"], "x": cube.coords["x"]},
                dims=["band", "time", "y", "x"],
                name="SpectralIndices"
            )

        # Append indices to the original cube
        cube = xr.concat([cube, indices_data_array], dim="band")

        # Update description
        if "description" in cube.attrs:
            cube.attrs["description"] += " + Spectral Indices"
        else:
            cube.attrs["description"] = "Spectral Indices"

        return cube

    
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
