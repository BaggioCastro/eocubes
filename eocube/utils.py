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

import json

import rasterio
import requests
from pyproj import CRS, Proj, transform


class Utils():

    def _response(self, url, json_obj=False, obj=None):
        """Get response JSON from url using object.

        Parameters

         - url <string, required>: The site or service url.

         - json_obj <boolean, optional>: If there is a JSON object to POST (default is False).

         - obj <dictionary, optional>: Request the JSON object for POST type, ignored if `json_obj` is False (default is None).

        Raise

         - HttpErrors: If the resquested url is not valid or not exist.
        """
        # Headers for request on POST by default
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        # Verify if json_obj exists by boolean key
        if json_obj:
            # Return the requested response from url
            return requests.post(url, data=json.dumps(obj), headers=headers).json()
        else:
            # Uses get if json_obj not exists
            return requests.get(url).json()

    def _validateBBOX(self, bbox):
        """Validate an input bounding box from user.

        Parameters

         - bbox <list of int, required>: An array with longitute e latitude of bounds [var_long_min, var_lat_min, var_long_max, var_lat_max].

        Raise

         - ValueError: If the resquested coordinate is invalid or not typed.
        """
        var_long_min, var_lat_min, var_long_max, var_lat_max = bbox

        if((var_long_min > 180) or (var_long_min < -180)):
            raise ValueError("Erro: o valor digitado é inválido.")

        else:
            if((var_lat_min > 90) or (var_lat_min < -90)):
                raise ValueError("Erro: o valor digitado é inválido.")
            else:
                if((var_long_min > 180) or (var_long_min < -180)):
                    raise ValueError("Erro: o valor digitado é inválido.")
                else:
                    if((var_lat_max > 90 ) or (var_lat_max < -90)):
                        raise ValueError("Erro: o valor digitado é inválido.")

        return True

    def _afimPointsToCoord(self, raster_file, x, y):
        """Calculate the long lat of a given point from band matrix.

        Parameters

         - raster_file <string, required>: The raster file path

         - x <int, required>: For colunms.

         - y <int, required>: For lines.

        Raise

         - ValueError: If the resquested coordinate is invalid or not typed.
        """
        with rasterio.open(raster_file) as dataset:
            coord = dataset.transform * (y, x)
            lon, lat = transform(
                dataset.crs.wkt,
                Proj(init=CRS.from_string("EPSG:4326")),
                coord[0], coord[1]
            )
        return (lon, lat)

    def _afimCoordsToPoint(self, raster_file, lon, lat):
        """Calculate the point of a given long lat from band matrix.

        Parameters

         - raster_file <string, required>: The raster file path

         - lon <float, required>: For longitude EPSG:4326.

         - lat <float, required>: For latitude EPSG:4326.

        Raise

         - ValueError: If the resquested coordinate is invalid or not typed.
        """
        with rasterio.open(raster_file) as dataset:
            coord = transform(
                Proj(init=CRS.from_string("EPSG:4326")),
                dataset.crs.wkt,
                lon, lat
            )
            x, y = rasterio.transform.rowcol(dataset.transform, coord[0], coord[1])
        return (x, y)
