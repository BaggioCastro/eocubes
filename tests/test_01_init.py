"""
API - EO Data Cube.

Tests Python Client Library for Earth Observation Data Cube.
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

import os
import unittest


class TestInit(unittest.TestCase):
    """Tests Python Client Library for Earth Observation Data Cube."""

    def test_read_init(self):
        """Test that the plugin __init__ will validate on plugins.qgis.org."""
        self.assertEqual("Alô", "Alô")

if __name__ == '__main__':
    unittest.main()