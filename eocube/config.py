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

Environment Variables

- BASE_DIR = os.path.abspath(os.path.dirname(__file__))
- EOCUBE_URL = "http://localhost:5000/eocube"
- STAC_URL = "https://brazildatacube.dpi.inpe.br/stac/"
- ACCESS_TOKEN = ""
"""

import os

# Save files base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# EO Cube Services
EOCUBE_URL = "http://localhost:5000/eocube"

# Brazil data cube services
STAC_URL = "https://brazildatacube.dpi.inpe.br/stac/"

# Access token for users
ACCESS_TOKEN = ""
