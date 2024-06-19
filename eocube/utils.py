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
import re
import numpy as np
import numba as nb


@nb.njit(parallel=True)
def apply_labels(predictions, labels):
    n = predictions.shape[0]
    output = np.empty_like(predictions)
    for i in nb.prange(n):
        output[i] = labels[predictions[i]]
    return output

def calculate_index(cubo, formula):
    # Encontrar todas as bandas BXX na fórmula
    band_names = set(re.findall(r'B\d{2}', formula))  
    
    # Substituir as bandas na fórmula pelo método de seleção do cubo
    temp_formula = formula
    for band_name in band_names:
        temp_formula = temp_formula.replace(band_name, f"cubo.sel(band='{band_name}')")
    
    # Avaliar a fórmula
    local_dict = {'cubo': cubo, 'np': np}
    result_data = eval(temp_formula, {}, local_dict)
    
    # Manter os atributos de dimensão do cubo original
    result_data.attrs['y_dim'] = cubo.attrs.get('y_dim')
    result_data.attrs['x_dim'] = cubo.attrs.get('x_dim')
    
    return result_data


def concatenate_bands(cubo):
    """
    Reformata um cubo de dados combinando as dimensões de banda e tempo.

    Parâmetros:
    - cubo: xarray.DataArray contendo as dimensões 'band', 'time', e 'pixel'.

    Retorna:
    - cubo_transposed: xarray.DataArray com 'pixel' como a primeira dimensão e 'band_time' como a segunda dimensão.
    """
    # Combinar as dimensões 'band' e 'time' em uma nova dimensão 'band_time'
    reshaped_cubo = cubo.stack(band_time=("band", "time"))

    # Transpor para obter 'pixel' como a primeira dimensão e 'band_time' como a segunda dimensão
    cubo_transposed = reshaped_cubo.transpose("pixel", "band_time")
    
    return cubo_transposed


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
    
    @staticmethod
    def safe_request(url: str, method: str = 'get', **kwargs) -> requests.Response:
        """Query the given URL for any HTTP Request and handle minimal HTTP Exceptions.

        :param url: The URL to query.
        :param method: HTTP Method name.
        :param kwargs: (optional) Any argument supported by `requests.request <https://docs.python-requests.org/en/latest/api/#requests.request>`_

        :raise HTTPError - For any HTTP error related.
        :raise ConnectionError - For any error related ConnectionError such InternetError

        :rtype: requests.Response
        """
        try:
            response = requests.request(method, url, **kwargs)

            response.raise_for_status()

            return response
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f'(Connection Refused) {e.request.url}')
        except requests.exceptions.HTTPError as e:
            if e.response is None:
                raise

            reason = e.response.reason
            msg = str(e)
            if e.response.status_code == 403:
                if e.request.headers.get('x-api-key') or 'access_token=' in e.request.url:
                    msg = "You don't have permission to request this resource."
                else:
                    msg = 'Missing Authentication Token.'  # TODO: Improve this message for any STAC provider.
            elif e.response.status_code == 500:
                msg = 'Could not request this resource.'

            raise requests.exceptions.HTTPError(f'({reason}) {msg}', request=e.request, response=e.response)

    @staticmethod
    def reproj_bbox(bbox,source_crs):
        from pyproj import CRS
        from pyproj import Transformer
        bdc_crs = CRS.from_wkt('PROJCS["unknown",GEOGCS["unknown",DATUM["Unknown based on GRS80 ellipsoid",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]]],PROJECTION["Albers_Conic_Equal_Area"],PARAMETER["latitude_of_center",-12],PARAMETER["longitude_of_center",-54],PARAMETER["standard_parallel_1",-2],PARAMETER["standard_parallel_2",-22],PARAMETER["false_easting",5000000],PARAMETER["false_northing",10000000],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH]]')
        inProj = CRS.from_epsg(source_crs)
        outProj = CRS.from_user_input(bdc_crs)
        transformer = Transformer.from_crs(inProj, outProj, always_xy=True)
        
        x1, y1, x2, y2 = bbox

        x1_reproj, y1_reproj = transformer.transform(x1, y1)
        x2_reproj, y2_reproj = transformer.transform(x2, y2)

        # Retorna o bbox reprojetado
        bbox_reproj = [x1_reproj, y1_reproj, x2_reproj, y2_reproj]
        
        return bbox_reproj
        
import matplotlib.pyplot as plt
import numpy as np
from ipywidgets import Button, HBox, VBox, Output, IntText, Checkbox, Dropdown, ColorPicker
import matplotlib.colors

def interactive_cluster_merging_with_timeseries(cubo, predictions):
    image_shape = (cubo.attrs['y_dim'], cubo.attrs['x_dim'])
    unique_clusters = np.unique(predictions)
    final_clusters = np.copy(predictions)
    cluster_map = {}
    cluster_colors = {}
    current_index = [0]

    output_area = Output()
    control_area = Output()
    start_button = Button(description='Iniciar')
    num_clusters_input = IntText(value=3, description='Número de Clusters Finais:')
    band_dropdown = Dropdown(options=cubo.band.values, description='Banda:', value='NDVI')
    forward_button = Button(description='Avançar', disabled=True, button_style='success')
    backward_button = Button(description='Voltar', disabled=True, button_style='warning')
    finalize_button = Button(description='Finalizar e Retornar', disabled=True)
    auto_advance_checkbox = Checkbox(value=True, description='Avançar Automaticamente', indent=False)

    # Inicializar color pickers e botões para cada cluster final
    cluster_buttons = [Button(description=f'Cluster Final {i}', disabled=False) for i in range(num_clusters_input.value)]
    color_pickers = [ColorPicker(value='blue', concise=True) for i in range(num_clusters_input.value)]

    # Agrupar botões e color pickers em linhas horizontais
    cluster_controls = [HBox([btn, picker]) for btn, picker in zip(cluster_buttons, color_pickers)]

    def update_plots():
        # Dados do cluster atual
        current_cluster_data = (predictions == unique_clusters[current_index[0]]).astype(int)
        reshaped_current_cluster = current_cluster_data.reshape(image_shape)
        reshaped_final_clusters = final_clusters.reshape(image_shape)
        
        # Série temporal do cluster atual
        indices = np.where(predictions == unique_clusters[current_index[0]])[0]
        cluster_series = cubo.sel(band=band_dropdown.value).values[indices] / 10000
        ts_mean = np.mean(cluster_series, axis=0)
        std_devs = np.std(cluster_series, axis=0)
        upper_limit = ts_mean + std_devs
        lower_limit = ts_mean - std_devs

        # Update color map
        unique_final_clusters = np.unique(final_clusters)
        colors = [cluster_colors.get(cluster, '#FFFFFF') for cluster in unique_final_clusters]
        cmap = matplotlib.colors.ListedColormap(colors)
        
        with output_area:
            output_area.clear_output(wait=True)
            fig, axs = plt.subplots(1, 3, figsize=(18, 6))
            axs[0].imshow(reshaped_current_cluster, cmap='gray_r', interpolation='none')
            axs[0].set_title('Cluster Atual')
            axs[1].imshow(reshaped_final_clusters, cmap=cmap, interpolation='none')
            axs[1].set_title('Preview da Integração dos Clusters')
            
            axs[2].plot(ts_mean, color='red', label='Média')
            axs[2].fill_between(range(len(ts_mean)), lower_limit, upper_limit, color='gray', alpha=0.5, label='Desvio Padrão')
            axs[2].set_title('Série Temporal do Cluster Atual')
            axs[2].legend()

            plt.tight_layout()
            plt.show()

    def start_integration(b):
        nonlocal cluster_buttons, color_pickers
        for i, button in enumerate(cluster_buttons):
            button.on_click(lambda b, idx=i: integrate_cluster(idx))
        finalize_button.disabled = False
        forward_button.disabled = False
        backward_button.disabled = False
        update_plots()
        control_area.clear_output()
        with control_area:
            display(HBox([backward_button, forward_button, auto_advance_checkbox]),
                    VBox(cluster_controls),
                    finalize_button)

    def integrate_cluster(cluster_idx):
        if current_index[0] < len(unique_clusters):
            final_clusters[predictions == unique_clusters[current_index[0]]] = cluster_idx
            cluster_map[unique_clusters[current_index[0]]] = cluster_idx
            cluster_colors[cluster_idx] = color_pickers[cluster_idx].value
            update_plots()
            if auto_advance_checkbox.value:
                forward_click(None)

    def forward_click(b):
        if current_index[0] < len(unique_clusters) - 1:
            current_index[0] += 1
            update_plots()

    def backward_click(b):
        if current_index[0] > 0:
            current_index[0] -= 1
            update_plots()

    def finalize_integration(b):
        with output_area:
            output_area.clear_output(wait=True)
            print("Integração Finalizada. Dados prontos para uso.")
            print("Mapeamento de Clusters:", cluster_map)

    start_button.on_click(start_integration)
    forward_button.on_click(forward_click)
    backward_button.on_click(backward_click)
    finalize_button.on_click(finalize_integration)

    display(VBox([HBox([num_clusters_input, band_dropdown, start_button]), control_area, output_area]))

    return final_clusters, cluster_map