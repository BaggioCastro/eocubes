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
from IPython.core.display import display, HTML
import ipywidgets as widgets


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
    #TODO concatenar janelas quando bbox intersecta 4 tiles
    # cubo = eodatacube.search(tile = '028022')
    # cubo2 = eodatacube.search(tile = '029022')
    # cubo3 = eodatacube.search(tile = '028023')
    # cubo4 = eodatacube.search(tile = '029023')
    # result1 = xr.concat([cubo, cubo2], dim='x')
    # result2 = xr.concat([cubo3, cubo4], dim='x')
    # result = xr.concat([result1, result2], dim='y')

    def __init__(self, collections: List[str], query_bands: List[str], 
                 start_date: str, end_date: str, limit: int = 30, tiles: List[str] = None,bbox: Tuple[float, float, float, float] = None,formulas: List[str] = None ):
        check_that(collections, msg="Please insert a list of available collections!")
        check_that(query_bands, msg="Please insert a list of available bands with query_bands!")
        #check_that(bbox, msg="Please insert a bounding box parameter!")


        self.utils = Utils()
        self.collections = collections
        self.query_bands = query_bands
        self.formulas = formulas
        self.bbox = bbox
        if self.bbox:
            self.bbox = self._validate_bbox(bbox)
        self.start_date, self.end_date = self._validate_dates(start_date, end_date)
        self.tiles = tiles

        self.stac_client = self._initialize_stac_client()
        self.stac_client.add_conforms_to("ITEM_SEARCH")
        self.stac_client.add_conforms_to("QUERY")
        self.timeline = []
        self.data_images = {}
        self.data_array = None

        

        items = self._search_stac(limit)
        self.xr_arrays = []
        self.n_tiles = []
        for item in items:
            images,bands_to_query = self._create_images_from_items(item)
            self.query_bands = bands_to_query
            if not images:
                raise ValueError("No data cube created!")

            self.data_images, self.data_array = self._build_data_array(images)
            self.n_tiles.append(self.tiles)
            self.xr_arrays.append(self.data_array)
        self.final_array = xr.concat(self.xr_arrays, dim = "tile")
        del self.data_array

    def __str__(self):
        collections_str = ', '.join(self.collections)
        query_bands_str = ', '.join(self.query_bands)
        formulas_str = '<br>'.join(
            f"<div style='border:1px solid #666; background-color: #f9f9f9; padding: 10px; margin: 5px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>{formula}</div>"
            for formula in self.formulas
        ) if self.formulas else "No forumula specified"
        tiles_str = ', '.join(self.n_tiles) if self.n_tiles else "No tiles specified"
        bbox_str = str(self.bbox) if self.bbox else "No bounding box specified"

        html = f"""
        <style>
            .datacube-table {{
                width: 80%;  /* Reduz a largura da tabela para 80% da largura do container */
                max-width: 800px;  /* Define uma largura máxima para evitar tabelas excessivamente grandes */
                margin-left: auto;
                margin-right: auto;  /* Centraliza a tabela horizontalmente */
                border-collapse: collapse;
            }}
            .datacube-table th, .datacube-table td {{
                padding: 8px;
                border: 1px solid #ddd;
                text-align: left;
            }}
            .datacube-table th {{
                background-color: #f4f4f4;
            }}
        </style>
        <table class="datacube-table">
            <tr><th>Attribute</th><th>Value</th></tr>
            <tr><td><b>Collections</b></td><td>{collections_str}</td></tr>
            <tr><td><b>Query Bands</b></td><td>{query_bands_str}</td></tr>
            <tr><td><b>Formulas</b></td><td>{formulas_str}</td></tr>
            <tr><td><b>Bounding Box</b></td><td>{bbox_str}</td></tr>
            <tr><td><b>Date Range</b></td><td>{self.start_date} to {self.end_date}</td></tr>
            <tr><td><b>Tiles</b></td><td>{tiles_str}</td></tr>
        </table>
        """
        return html


    def display(self):
        display(HTML(self.__str__()))
        # Criando a interação para a timeline
        count_label = widgets.Label(value=f"Number of dates in timeline: {len(self.timeline)}")
        display(count_label)
        timeline_widget = widgets.SelectMultiple(
            options=self.timeline,
            value=[self.timeline[0]],
            description='Timeline:',
            disabled=False
        )
        display(timeline_widget)

    def display_summary(self):
        # Display the HTML summary
        display(HTML(self.__str__()))


    def _initialize_stac_client(self):
        parameters = dict(access_token=config.ACCESS_TOKEN)
        return pystac_client.Client.open(config.STAC_URL, parameters=parameters)

    def _validate_bbox(self, bbox):
        check_bbox_format(bbox, msg="Invalid bounding box parameter!")
        return bbox

    def _validate_dates(self, start_date: str, end_date: str):
        check_date_range(start_date, end_date)
        return start_date, end_date

    def _search_stac(self, limit=100):
        try:
            # Decide se deve buscar por bbox ou tiles
            if self.bbox:
                # Busca usando bbox
                item_search = self.stac_client.search(
                    collections=self.collections,
                    bbox=self.bbox,
                    datetime=f'{self.start_date}/{self.end_date}',
                    limit=limit
                )
            elif self.tiles:
                # Busca usando query para tiles
                item_search = self.stac_client.search(
                    query={"bdc:tile": {"in": self.tiles}},
                    datetime=f'{self.start_date}/{self.end_date}',
                    collections=self.collections,
                    limit=limit
                )
            else:
                # Retorna uma mensagem de erro ou lança uma exceção se nem bbox nem tiles forem fornecidos
                raise ValueError("Either 'bbox' or 'tiles' must be specified for searching.")
            
            # Processa os resultados da busca
            items = list(item_search.items())
            pattern = re.compile(r"_(\d{6})_\d{8}$")
            unique_tiles = sorted({pattern.findall(item.id)[0] for item in items if pattern.findall(item.id)})
            return [[item for item in items if tile in item.id] for tile in unique_tiles]
        except Exception as e:
            logging.error("Failed to search STAC service.", exc_info=True)
            raise RuntimeError("Connection refused!") from e

    def _extract_bands(self, formulas):
        band_pattern = re.compile(r'B\d{2}')
        return sorted(set(band_pattern.findall(' '.join(formulas))))

    
    def _create_images_from_items(self, items):
        images = []
        if self.formulas:
            bands_to_query_set = set(self.query_bands) | set(self._extract_bands(self.formulas))
        else:
            bands_to_query_set = set(self.query_bands)

        if items:
            for item in items:
                available_bands = sorted([band for band in list(item.assets.keys())])
                bands_to_query = [band for band in available_bands if band in bands_to_query_set]
             
                if all(band in available_bands for band in bands_to_query_set):
                    images.append(Image(item=item, bands=bands_to_query, bbox=self.bbox))
                else:
                    missing_bands = bands_to_query_set - set(available_bands)
                    print(f"As seguintes bandas a serem consultadas não estão disponíveis no item: {missing_bands}")

        return images, bands_to_query
    
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
        self.tiles = image.tile

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
            coords={"band": self.query_bands, "time": self.timeline, "tile":  self.tiles},
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
               as_time_series: bool = False, tile: Optional[str] = None):
        """Search method to retrieve data from delayed dataset and return all dataset for black searches but takes longer.

        Parameters:
        - band <string, optional>: The common name of band (nir, ndvi, red, ... see info.collections).
        - start_date <string, optional>: The string start date formatted "yyyy-mm-dd" to complete the interval.
        - end_date <string, optional>: The string end date formatted "yyyy-mm-dd" to complete the interval and retrieve a dataset.
        - as_time_series <bool, optional>: If True, return the result as a time series.
        - formulas <list of string, optional>: Formulas to calculate additional indices.

        Raise:
        - KeyError: If the given parameter does not exist.
        """
        _start_date = self.start_date
        _end_date = self.end_date
        _bands = self.query_bands
        _timeline = self.timeline
        _formulas = self.formulas

        if tile:
            self.data_array = self.final_array.sel(tile = tile)
        else:
            self.data_array = self.final_array.isel(tile = 0)

        tasks = [self.data_array.loc[band, _start_date:_end_date].values for band in _bands]

        computed_data = compute(*[item for sublist in tasks for item in sublist])

        _data = np.array([computed_data[i:i+len(_timeline)] for i in range(0, len(computed_data), len(_timeline))])
        
        del computed_data

        bandas = _bands.copy()

        if _formulas:
            # Calcule os valores das bandas e armazene em band_values
            for formula in _formulas:
                filter_bands = self._extract_bands([formula])

                band_values = {band: _data[idx] for idx, band in enumerate(_bands) if band in filter_bands}
                try:
                    # Calculate the index value directly from the band_values dictionary
                    index_value = eval(formula, {}, band_values)
                    _data = np.concatenate((_data, np.expand_dims(np.squeeze(index_value).astype("int16"), axis=0)), axis=0)
                    bandas.append(formula)
                except NameError as e:
                    print(f"Error: {e}. Please check the input bands and formulas.")
                    return None

        if as_time_series:
            result = self.cube_to_time_series(_data, bandas, _timeline)
        else:
            result = xr.DataArray(
                _data,
                coords={"band": bandas, "time": _timeline, "y": range(_data.shape[2]), "x": range(_data.shape[3])},
                dims=["band", "time", "y", "x"],
                name="DataCube"
            )

        #result.attrs['product'] = self.description
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


    def interactPlot(self, method: str):
        #todo fazer receber qualquer composição e retornar um tif com um mos
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
