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


import numpy as np


class Spectral():
    """Abstraction to deal with indexes and operations related to image processing."""

    def _normalize(self, array):
        """Normalize numpy arrays into scale 0.0 - 1.0.

        Parameters

         - array <nparray, required>: The nparray multidimensional for normalize

        Raise

         - ValueError: If the resquested nparray is invalid or not typed.
        """
        # Using techniques from statistics for normalize
        array_min, array_max = array.min(), array.max()
        return ((array - array_min)/(array_max - array_min))

    def _ndvi(self, nir, red, cte_delta=1e-10):
        """Calculate the Normalized Difference Vegetation Index - NDVI.

        Parameters

         - nir <np.array, required>: A multidimensional nparray with next infrared values.

         - red <np.arrary, required>: A multidimensional nparray with band red values.

         - cte_delta <float, optional>: A float number to prevent zero values on formula.

        Raise

         - ValueError: If the resquested nparray is invalid or not typed.
        """
        # Função para cálculo do índice NDVI
        ndvi = (nir - red) / (nir + red + cte_delta)
        return ndvi

    def _ndwi(self, nir, green, cte_delta=1e-10):
        """Calculate the Normalized Difference Water Index - NDWI.

        Parameters

         - nir <np.array, required>: A multidimensional nparray with next infrared values.

         - green <np.arrary, required>: A multidimensional nparray with band green values.

         - cte_delta <float, optional>: A float number to prevent zero values on formula.

        Raise

         - ValueError: If the resquested nparray is invalid or not typed.
        """
        # Função para cálculo do índice NDWI
        ndwi = (green - nir) / (green + nir + cte_delta)
        return ndwi

    def _ndbi(self, nir, swir1, cte_delta=1e-10):
        """Calculate the Normalized Difference Built-up Index - NDBI.

        Parameters

         - nir <np.array, required>: A multidimensional nparray with next infrared values.

         - swir1 <np.arrary, required>: A multidimensional nparray with band swir1 values.

         - cte_delta <float, optional>: A float number to prevent zero values on formula.

        Raise

         - ValueError: If the resquested nparray is invalid or not typed.
        """
        # Função para cálculo do índice NDBI
        ndbi = (swir1 - nir) / (swir1 + nir + cte_delta)
        return ndbi

    def _rgb(self, red, green, blue):
        """Calculate the real color composition from image.

        Parameters

         - red <np.array, required>: A multidimensional nparray with red values.

         - green <np.arrary, required>: A multidimensional nparray with band green values.

         - blue <np.array, required>: A multidimensional nparray with band blue values.

        Raise

         - ValueError: If the resquested nparray is invalid or not typed.
        """
        # Função para cálculo para a visualização da cor real da imagem
        linhas = blue.shape[0]
        colunas = blue.shape[1]
        array_rgb = np.zeros((linhas, colunas, 3))
        array_rgb[:, :, 0] = red / red.max()
        array_rgb[:, :, 1] = green / green.max()
        array_rgb[:, :, 2] = blue / blue.max()
        return array_rgb

    def _format(self, matrix):
        """Preprocessing matrix formating all data to float.

        Parameters

         - matrix <np.array, required>: A multidimensional matrix.

        Raise

         - ValueError: If the given matrix is not correctly formated.
        """
        # Função para pré-processar matrizes
        return matrix.astype(float)

    def _validate_shape(self, matrix_t1, matrix_t2):
        """Verify if two matrixes have the same dimension.

        Parameters

         - matrix_t1 <np.array, required>: A multidimensional matrix.

         - matrix_t2 <np.array, required>: A multidimensional matrix.

        Raise

         - ValueError: If the given matrix is not correctly formated.
        """
        # Função para verificar se as dimensões das matrizes são equivalentes
        return matrix_t1.shape == matrix_t2.shape

    def _matrix_diff(self, matrix_t1, matrix_t2):
        """Calculate the arithmetic difference (matrix_t1 - matrix_t).

        Parameters

         - matrix_t1 <np.array, required>: A multidimensional matrix.

         - matrix_t2 <np.array, required>: A multidimensional matrix.

        Raise

         - ValueError: If the given matrix is not correctly formated.
        """
        # Função para cálculo das diferenças entre duas matrizes
        _result = matrix_t2 - matrix_t1
        return _result

    def _classify_diff(self, _result, limiar_min=0, limiar_max=0):
        """Classify difference based on limiar min and max.

        Parameters

         - _result <np.array, required>: A multidimensional matrix with arithmetic difference.

         - limiar_min <float, required>: The minimum value classified to difference.

         - limiar_max <float, required>: The maximum value classified to difference to complete the interval.

        Raise

         - ValueError: If the given matrix is not correctly formated.
        """
        # Função para classificar as diferenças de uma matriz
        if limiar_min > 0:
            raise Exception("LimiarMin Inválido")
        if limiar_max < 0:
            raise Exception("LimiarMax Inválido")
        # Criar uma matriz de zeros (com o mesmo shape da matriz resultante)
        # limiar_min <= |_result| <= limiar_max
        # Critério de mudança:
        # As matrizes são consideradas iguais ou muito semelhantes
        # As matrizes sofreram "grandes" alterações
        return np.where(_result <= limiar_min, 0, np.where(_result <= limiar_max, 1, 0))
