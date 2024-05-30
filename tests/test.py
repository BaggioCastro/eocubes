from eocube import DataCube, info, config, interpolate
config.ACCESS_TOKEN = 'QEgHMsFRLNTwqisIHW0pZMsD0niPwIPbuxdePzAvHJ'
config.STAC_URL = 'https://brazildatacube.dpi.inpe.br/stac/'

eodatacube = DataCube(
    collections=["S2-16D-2"],
    query_bands=['B03', 'B04','B8A', 'B11','NDVI','NBR', 'SCL'],
    formulas = ['((B03-B11)/(B03+B11))',
                '(4 * (B03 - B11)) - (0.25 * B08) + (2.75 * B11)',
               ' ((B08 - B04) / (B08 + B04 + (1*10000))) * ((2*10000))'],
    bbox=[-67.6910,-9.9748,-67.6545,-9.9548],
    start_date="2021-05-09",
    end_date="2021-12-29",
    limit=50,
    window = False
)

#cubo = eodatacube.search(as_time_series=True)