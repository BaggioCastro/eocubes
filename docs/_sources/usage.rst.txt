..
    This file is part of Python Client Library for Earth Observation Data Cube.
    Copyright (C) 2021 None.

    Python Client Library for Earth Observation Data Cube is free software;
    You can redistribute it and/or modify it under the terms of the MIT License;
    See LICENSE file for more details.

=====================
Usando a API - EOCube
=====================

O pacote EOCube permite que o usuário realize buscas por imagens de
sensoriamento remoto com a criação de cubos de dados utilizando as
matrizes indexadas com *Xarray*. Para isso o usuário necessita apenas de
um código de acesso do projeto *BDC* e selecionar alguns parâmetros como
as coleções de dados baseadas nos conjuntos de imagens dos satélites,
uma área de interesse em formato de limites em coordenadas de dois
pontos no mapa denominado *Bounding Box*, as bandas espectrais como o
infravermelho próximo ou espectros visíveis como azul, verde e vermelho,
o período de tempo a partir de duas datas definindo uma linha temporal e
por último se necessário um limite para quantidade de imagens no retorno
da busca.

Acessando dados de observação da Terra com a API - EOCubes
----------------------------------------------------------

Para iniciar nosso estudo de caso precisando importar as bibliotecas
necessárias como a ``matplotlib`` para visualizar os dados de forma
gráfica e customizar a visualização das imagens.

Logo, importanmos a biblioteca ``DataCube`` do pacote *EOCube*
juntamente com a biblioteca ``info`` para o retorno das informações do
*STAC* e a bibloteca ``config`` para configurar nossas variáveis de
ambiente.

Como utilizaremos o serviço *STAC* do Projeto *Brazil Data Cube - BDC*
não necessitamos alterar o ``config.STAC_URL`` para outros servidores.

Então vamos inserir o *token* de acesso adiquirido pelo *site* de
autenticação `BDC
Auth <https://brazildatacube.dpi.inpe.br/auth/v1/auth/login>`__ do
projeto *BDC*.

.. code:: ipython3

    import matplotlib as mpl
    import matplotlib.pyplot as plt
    %matplotlib inline
    
    from eocube import DataCube, info, config
    
    config.ACCESS_TOKEN = "<seu_token>"

Recuperando os metadados
~~~~~~~~~~~~~~~~~~~~~~~~

Agora que importamos as bibliotecas necessárias podemos criar um cubo de
dados para o estudo de caso.

Mas antes vamos recuperar as coleções de dados disponíveis para a
criação do Cubo com o método ``info.collections()``:

.. code:: ipython3

    info.collections()




.. raw:: html

    <p>STAC</p>
                        <ul>
                         <li><b>URL:</b> https://brazildatacube.dpi.inpe.br/stac/</li>
                         <li><b>Collections:</b></li>
                         <ul>
                         <li>S2-MOSAIC-PARAIBA_10_3M_STK-1</li><li>CB4-MOSAIC-BRAZIL_64_3M_STK-1</li><li>MOD13Q1-6</li><li>CB4A-MOSAIC-PARAIBA_55_3M_STK-1</li><li>CB4MUX_20-1</li><li>LC8SR-1</li><li>S2_L1C-1</li><li>CB4MUX_20_1M_STK-1</li><li>LC8_30-1</li><li>S2_MSI_L2_SR_LASRC-1</li><li>LC8_DN-1</li><li>KD_S2_20M_VISBANDS_CURUAI-1</li><li>LC8_30_6M_MEDSTK-1</li><li>LC8-MOSAIC-BRAZIL_30_6M_MEDSTK-1</li><li>MYD13Q1-6</li><li>LC8_30_16D_STK-1</li><li>CB4_64_16D_STK-1</li><li>CB4_64-1</li><li>CB4_20_1M_STK-1</li><li>S2_10_16D_STK-1</li><li>S2-SEN2COR_10_16D_STK-1</li><li>LCC_C4_64_1M_STK_PA-SPC-AC-NA-1</li><li>LCC_S2_10_1M_STK_PA-SPC-AC-NA-1</li><li>LCC_L8_30_1M_STK_PA-SPC-AC-NA-1</li><li>S2_10-1</li><li>CB4-MUX-L4-SR-CMPAC-COG-1</li><li>LCC_C4_64_1M_STK_MT_PA-SPC-AC-NA-1</li><li>LCC_C4_64_1M_STK_GO_PA-SPC-AC-NA-1</li><li>LCC_C4_64_1M_STK_MT_RF_PA-SPC-AC-NA-1</li>
                         </ul>
                       </ul>




Bom para fins de estudo utilizaremos apenas a coleção
``CB4_64_16D_STK-1`` pois possui as bandas espectrais necessárias para a
exploração dos dados pelo pacote *EOCube*.

Então vamos recuperar os metadados referentes a esta coleção com o
método ``info.describe``:

.. code:: ipython3

    info.describe("CB4_64_16D_STK-1")




.. raw:: html

    <div>
        <b>Collection:</b> CB4_64_16D_STK-1
    </div>
    <div>
        <b>Description:</b> This datacube was generated with all available surface reflectance images from CB4_64 cube. The data is provided with 64 meters of spatial resolution, reprojected and cropped to BDC_LG grid, considering a temporal compositing function of 16 days using the best pixel approach (Stack).
    </div>
    <div>
        <b>Start date:</b> 2016-01-01T00:00:00
        <b>End date:</b> 2021-02-17T00:00:00
    </div>
    <div>
        <b>STAC Version:</b> 0.9.0
    </div>
    </br>
    
    <b>Bands</b>
    <div>
        <table>
            <tr>
            </tr>
            <tr>
                <th>name</th>
                <th>common_name</th>
                <th>min</th>
                <th>max</th>
                <th>nodata</th>
                <th>scale</th>
                <th>data_type</th>
            </tr>
    
            <tr>
                <td>BAND13</td>
                <td>blue</td>
                <td>0.0</td>
                <td>10000.0</td>
                <td>-9999.0</td>
                <td>0.0001</td>
                <td>int16</td>
            </tr>
    
            <tr>
                <td>BAND14</td>
                <td>green</td>
                <td>0.0</td>
                <td>10000.0</td>
                <td>-9999.0</td>
                <td>0.0001</td>
                <td>int16</td>
            </tr>
    
            <tr>
                <td>BAND15</td>
                <td>red</td>
                <td>0.0</td>
                <td>10000.0</td>
                <td>-9999.0</td>
                <td>0.0001</td>
                <td>int16</td>
            </tr>
    
            <tr>
                <td>BAND16</td>
                <td>nir</td>
                <td>0.0</td>
                <td>10000.0</td>
                <td>-9999.0</td>
                <td>0.0001</td>
                <td>int16</td>
            </tr>
    
            <tr>
                <td>CLEAROB</td>
                <td>ClearOb</td>
                <td>1.0</td>
                <td>255.0</td>
                <td>0.0</td>
                <td>1.0</td>
                <td>uint8</td>
            </tr>
    
            <tr>
                <td>CMASK</td>
                <td>quality</td>
                <td>0.0</td>
                <td>4.0</td>
                <td>255.0</td>
                <td>1.0</td>
                <td>uint8</td>
            </tr>
    
            <tr>
                <td>EVI</td>
                <td>evi</td>
                <td>-10000.0</td>
                <td>10000.0</td>
                <td>-9999.0</td>
                <td>0.0001</td>
                <td>int16</td>
            </tr>
    
            <tr>
                <td>NDVI</td>
                <td>ndvi</td>
                <td>-10000.0</td>
                <td>10000.0</td>
                <td>-9999.0</td>
                <td>0.0001</td>
                <td>int16</td>
            </tr>
    
            <tr>
                <td>PROVENANCE</td>
                <td>Provenance</td>
                <td>1.0</td>
                <td>366.0</td>
                <td>-1.0</td>
                <td>1.0</td>
                <td>int16</td>
            </tr>
    
            <tr>
                <td>TOTALOB</td>
                <td>TotalOb</td>
                <td>1.0</td>
                <td>255.0</td>
                <td>0.0</td>
                <td>1.0</td>
                <td>uint8</td>
            </tr>
    
        </table>
    </div>
    </br>
    
    <div>
        <b>Extent</b>
    </div>
    <div>
        <table>
            <tr>
                <th>xmin</th>
                <th>ymin</th>
                <th>xmax</th>
                <th>ymax</th>
            </tr>
            <tr>
                <td>-79.267539</td>
                <td>-35.241045</td>
                <td>-29.421667</td>
                <td>9.14676</td>
            </tr>
        </table>
    </div>
    </br>
    
    <div>
        <div><b>Timeline</b></div>
        <select id="timeline" size="10">
    
            <option value="2016-01-01">2016-01-01</option>\n
    
            <option value="2016-01-16">2016-01-16</option>\n
    
            <option value="2016-01-17">2016-01-17</option>\n
    
            <option value="2016-02-01">2016-02-01</option>\n
    
            <option value="2016-02-02">2016-02-02</option>\n
    
            <option value="2016-02-17">2016-02-17</option>\n
    
            <option value="2016-02-18">2016-02-18</option>\n
    
            <option value="2016-03-04">2016-03-04</option>\n
    
            <option value="2016-03-05">2016-03-05</option>\n
    
            <option value="2016-03-20">2016-03-20</option>\n
    
            <option value="2016-03-21">2016-03-21</option>\n
    
            <option value="2016-04-05">2016-04-05</option>\n
    
            <option value="2016-04-06">2016-04-06</option>\n
    
            <option value="2016-04-21">2016-04-21</option>\n
    
            <option value="2016-04-22">2016-04-22</option>\n
    
            <option value="2016-05-07">2016-05-07</option>\n
    
            <option value="2016-05-08">2016-05-08</option>\n
    
            <option value="2016-05-23">2016-05-23</option>\n
    
            <option value="2016-05-24">2016-05-24</option>\n
    
            <option value="2016-06-08">2016-06-08</option>\n
    
            <option value="2016-06-09">2016-06-09</option>\n
    
            <option value="2016-06-24">2016-06-24</option>\n
    
            <option value="2016-06-25">2016-06-25</option>\n
    
            <option value="2016-07-10">2016-07-10</option>\n
    
            <option value="2016-07-11">2016-07-11</option>\n
    
            <option value="2016-07-26">2016-07-26</option>\n
    
            <option value="2016-07-27">2016-07-27</option>\n
    
            <option value="2016-08-11">2016-08-11</option>\n
    
            <option value="2016-08-12">2016-08-12</option>\n
    
            <option value="2016-08-27">2016-08-27</option>\n
    
            <option value="2016-08-28">2016-08-28</option>\n
    
            <option value="2016-09-12">2016-09-12</option>\n
    
            <option value="2016-09-13">2016-09-13</option>\n
    
            <option value="2016-09-28">2016-09-28</option>\n
    
            <option value="2016-09-29">2016-09-29</option>\n
    
            <option value="2016-10-14">2016-10-14</option>\n
    
            <option value="2016-10-15">2016-10-15</option>\n
    
            <option value="2016-10-30">2016-10-30</option>\n
    
            <option value="2016-10-31">2016-10-31</option>\n
    
            <option value="2016-11-15">2016-11-15</option>\n
    
            <option value="2016-11-16">2016-11-16</option>\n
    
            <option value="2016-12-01">2016-12-01</option>\n
    
            <option value="2016-12-02">2016-12-02</option>\n
    
            <option value="2016-12-17">2016-12-17</option>\n
    
            <option value="2016-12-18">2016-12-18</option>\n
    
            <option value="2016-12-31">2016-12-31</option>\n
    
            <option value="2017-01-01">2017-01-01</option>\n
    
            <option value="2017-01-16">2017-01-16</option>\n
    
            <option value="2017-01-17">2017-01-17</option>\n
    
            <option value="2017-02-01">2017-02-01</option>\n
    
            <option value="2017-02-02">2017-02-02</option>\n
    
            <option value="2017-02-17">2017-02-17</option>\n
    
            <option value="2017-02-18">2017-02-18</option>\n
    
            <option value="2017-03-05">2017-03-05</option>\n
    
            <option value="2017-03-06">2017-03-06</option>\n
    
            <option value="2017-03-21">2017-03-21</option>\n
    
            <option value="2017-03-22">2017-03-22</option>\n
    
            <option value="2017-04-06">2017-04-06</option>\n
    
            <option value="2017-04-07">2017-04-07</option>\n
    
            <option value="2017-04-22">2017-04-22</option>\n
    
            <option value="2017-04-23">2017-04-23</option>\n
    
            <option value="2017-05-08">2017-05-08</option>\n
    
            <option value="2017-05-09">2017-05-09</option>\n
    
            <option value="2017-05-24">2017-05-24</option>\n
    
            <option value="2017-05-25">2017-05-25</option>\n
    
            <option value="2017-06-09">2017-06-09</option>\n
    
            <option value="2017-06-10">2017-06-10</option>\n
    
            <option value="2017-06-25">2017-06-25</option>\n
    
            <option value="2017-06-26">2017-06-26</option>\n
    
            <option value="2017-07-11">2017-07-11</option>\n
    
            <option value="2017-07-12">2017-07-12</option>\n
    
            <option value="2017-07-27">2017-07-27</option>\n
    
            <option value="2017-07-28">2017-07-28</option>\n
    
            <option value="2017-08-12">2017-08-12</option>\n
    
            <option value="2017-08-13">2017-08-13</option>\n
    
            <option value="2017-08-28">2017-08-28</option>\n
    
            <option value="2017-08-29">2017-08-29</option>\n
    
            <option value="2017-09-13">2017-09-13</option>\n
    
            <option value="2017-09-14">2017-09-14</option>\n
    
            <option value="2017-09-29">2017-09-29</option>\n
    
            <option value="2017-09-30">2017-09-30</option>\n
    
            <option value="2017-10-15">2017-10-15</option>\n
    
            <option value="2017-10-16">2017-10-16</option>\n
    
            <option value="2017-10-31">2017-10-31</option>\n
    
            <option value="2017-11-01">2017-11-01</option>\n
    
            <option value="2017-11-16">2017-11-16</option>\n
    
            <option value="2017-11-17">2017-11-17</option>\n
    
            <option value="2017-12-02">2017-12-02</option>\n
    
            <option value="2017-12-03">2017-12-03</option>\n
    
            <option value="2017-12-18">2017-12-18</option>\n
    
            <option value="2017-12-19">2017-12-19</option>\n
    
            <option value="2017-12-31">2017-12-31</option>\n
    
            <option value="2018-01-01">2018-01-01</option>\n
    
            <option value="2018-01-16">2018-01-16</option>\n
    
            <option value="2018-01-17">2018-01-17</option>\n
    
            <option value="2018-02-01">2018-02-01</option>\n
    
            <option value="2018-02-02">2018-02-02</option>\n
    
            <option value="2018-02-17">2018-02-17</option>\n
    
            <option value="2018-02-18">2018-02-18</option>\n
    
            <option value="2018-03-05">2018-03-05</option>\n
    
            <option value="2018-03-06">2018-03-06</option>\n
    
            <option value="2018-03-21">2018-03-21</option>\n
    
            <option value="2018-03-22">2018-03-22</option>\n
    
            <option value="2018-04-06">2018-04-06</option>\n
    
            <option value="2018-04-07">2018-04-07</option>\n
    
            <option value="2018-04-22">2018-04-22</option>\n
    
            <option value="2018-04-23">2018-04-23</option>\n
    
            <option value="2018-05-08">2018-05-08</option>\n
    
            <option value="2018-05-09">2018-05-09</option>\n
    
            <option value="2018-05-24">2018-05-24</option>\n
    
            <option value="2018-05-25">2018-05-25</option>\n
    
            <option value="2018-06-09">2018-06-09</option>\n
    
            <option value="2018-06-10">2018-06-10</option>\n
    
            <option value="2018-06-25">2018-06-25</option>\n
    
            <option value="2018-06-26">2018-06-26</option>\n
    
            <option value="2018-07-11">2018-07-11</option>\n
    
            <option value="2018-07-12">2018-07-12</option>\n
    
            <option value="2018-07-27">2018-07-27</option>\n
    
            <option value="2018-07-28">2018-07-28</option>\n
    
            <option value="2018-08-12">2018-08-12</option>\n
    
            <option value="2018-08-13">2018-08-13</option>\n
    
            <option value="2018-08-28">2018-08-28</option>\n
    
            <option value="2018-08-29">2018-08-29</option>\n
    
            <option value="2018-09-13">2018-09-13</option>\n
    
            <option value="2018-09-14">2018-09-14</option>\n
    
            <option value="2018-09-29">2018-09-29</option>\n
    
            <option value="2018-09-30">2018-09-30</option>\n
    
            <option value="2018-10-15">2018-10-15</option>\n
    
            <option value="2018-10-16">2018-10-16</option>\n
    
            <option value="2018-10-31">2018-10-31</option>\n
    
            <option value="2018-11-01">2018-11-01</option>\n
    
            <option value="2018-11-16">2018-11-16</option>\n
    
            <option value="2018-11-17">2018-11-17</option>\n
    
            <option value="2018-12-02">2018-12-02</option>\n
    
            <option value="2018-12-03">2018-12-03</option>\n
    
            <option value="2018-12-18">2018-12-18</option>\n
    
            <option value="2018-12-19">2018-12-19</option>\n
    
            <option value="2018-12-31">2018-12-31</option>\n
    
            <option value="2019-01-01">2019-01-01</option>\n
    
            <option value="2019-01-16">2019-01-16</option>\n
    
            <option value="2019-01-17">2019-01-17</option>\n
    
            <option value="2019-02-01">2019-02-01</option>\n
    
            <option value="2019-02-02">2019-02-02</option>\n
    
            <option value="2019-02-17">2019-02-17</option>\n
    
            <option value="2019-02-18">2019-02-18</option>\n
    
            <option value="2019-03-05">2019-03-05</option>\n
    
            <option value="2019-03-06">2019-03-06</option>\n
    
            <option value="2019-03-21">2019-03-21</option>\n
    
            <option value="2019-03-22">2019-03-22</option>\n
    
            <option value="2019-04-06">2019-04-06</option>\n
    
            <option value="2019-04-07">2019-04-07</option>\n
    
            <option value="2019-04-22">2019-04-22</option>\n
    
            <option value="2019-04-23">2019-04-23</option>\n
    
            <option value="2019-05-08">2019-05-08</option>\n
    
            <option value="2019-05-09">2019-05-09</option>\n
    
            <option value="2019-05-24">2019-05-24</option>\n
    
            <option value="2019-05-25">2019-05-25</option>\n
    
            <option value="2019-06-09">2019-06-09</option>\n
    
            <option value="2019-06-10">2019-06-10</option>\n
    
            <option value="2019-06-25">2019-06-25</option>\n
    
            <option value="2019-06-26">2019-06-26</option>\n
    
            <option value="2019-07-11">2019-07-11</option>\n
    
            <option value="2019-07-12">2019-07-12</option>\n
    
            <option value="2019-07-27">2019-07-27</option>\n
    
            <option value="2019-07-28">2019-07-28</option>\n
    
            <option value="2019-08-12">2019-08-12</option>\n
    
            <option value="2019-08-13">2019-08-13</option>\n
    
            <option value="2019-08-28">2019-08-28</option>\n
    
            <option value="2019-08-29">2019-08-29</option>\n
    
            <option value="2019-09-13">2019-09-13</option>\n
    
            <option value="2019-09-14">2019-09-14</option>\n
    
            <option value="2019-09-29">2019-09-29</option>\n
    
            <option value="2019-09-30">2019-09-30</option>\n
    
            <option value="2019-10-15">2019-10-15</option>\n
    
            <option value="2019-10-16">2019-10-16</option>\n
    
            <option value="2019-10-31">2019-10-31</option>\n
    
            <option value="2019-11-01">2019-11-01</option>\n
    
            <option value="2019-11-16">2019-11-16</option>\n
    
            <option value="2019-11-17">2019-11-17</option>\n
    
            <option value="2019-12-02">2019-12-02</option>\n
    
            <option value="2019-12-03">2019-12-03</option>\n
    
            <option value="2019-12-18">2019-12-18</option>\n
    
            <option value="2019-12-19">2019-12-19</option>\n
    
            <option value="2019-12-31">2019-12-31</option>\n
    
            <option value="2020-01-01">2020-01-01</option>\n
    
            <option value="2020-01-16">2020-01-16</option>\n
    
            <option value="2020-01-17">2020-01-17</option>\n
    
            <option value="2020-02-01">2020-02-01</option>\n
    
            <option value="2020-02-02">2020-02-02</option>\n
    
            <option value="2020-02-17">2020-02-17</option>\n
    
            <option value="2020-02-18">2020-02-18</option>\n
    
            <option value="2020-03-04">2020-03-04</option>\n
    
            <option value="2020-03-05">2020-03-05</option>\n
    
            <option value="2020-03-20">2020-03-20</option>\n
    
            <option value="2020-03-21">2020-03-21</option>\n
    
            <option value="2020-04-05">2020-04-05</option>\n
    
            <option value="2020-04-06">2020-04-06</option>\n
    
            <option value="2020-04-21">2020-04-21</option>\n
    
            <option value="2020-04-22">2020-04-22</option>\n
    
            <option value="2020-05-07">2020-05-07</option>\n
    
            <option value="2020-05-08">2020-05-08</option>\n
    
            <option value="2020-05-23">2020-05-23</option>\n
    
            <option value="2020-05-24">2020-05-24</option>\n
    
            <option value="2020-06-08">2020-06-08</option>\n
    
            <option value="2020-06-09">2020-06-09</option>\n
    
            <option value="2020-06-24">2020-06-24</option>\n
    
            <option value="2020-06-25">2020-06-25</option>\n
    
            <option value="2020-07-10">2020-07-10</option>\n
    
            <option value="2020-07-11">2020-07-11</option>\n
    
            <option value="2020-07-26">2020-07-26</option>\n
    
            <option value="2020-07-27">2020-07-27</option>\n
    
            <option value="2020-07-31">2020-07-31</option>\n
    
            <option value="2020-08-12">2020-08-12</option>\n
    
            <option value="2020-08-27">2020-08-27</option>\n
    
            <option value="2020-08-28">2020-08-28</option>\n
    
            <option value="2020-09-12">2020-09-12</option>\n
    
            <option value="2020-09-13">2020-09-13</option>\n
    
            <option value="2020-09-28">2020-09-28</option>\n
    
            <option value="2020-09-29">2020-09-29</option>\n
    
            <option value="2020-10-14">2020-10-14</option>\n
    
            <option value="2020-10-15">2020-10-15</option>\n
    
            <option value="2020-10-30">2020-10-30</option>\n
    
            <option value="2020-10-31">2020-10-31</option>\n
    
            <option value="2020-11-15">2020-11-15</option>\n
    
            <option value="2020-11-16">2020-11-16</option>\n
    
            <option value="2020-12-01">2020-12-01</option>\n
    
            <option value="2020-12-02">2020-12-02</option>\n
    
            <option value="2020-12-17">2020-12-17</option>\n
    
            <option value="2020-12-18">2020-12-18</option>\n
    
            <option value="2020-12-31">2020-12-31</option>\n
    
            <option value="2021-01-01">2021-01-01</option>\n
    
            <option value="2021-01-16">2021-01-16</option>\n
    
            <option value="2021-01-17">2021-01-17</option>\n
    
            <option value="2021-02-01">2021-02-01</option>\n
    
            <option value="2021-02-02">2021-02-02</option>\n
    
            <option value="2021-02-17">2021-02-17</option>\n
    
        </select>
    </div>




Criação do Cubo de Dados de Exemplo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Com esta reposta podemos visualizar os atributos necessários para a
criação do cubo com a coleção selecionada, é possível criar cubos com
várias coleções através no tempo, mas para este caso utilizaremos apenas
a coleção do satélite *CBERS 4A*. Para compreender os filtros de dados,
a seguir temos algumas definições:

Collection
^^^^^^^^^^

Uma *collection* representa uma coleção de dados. Abaixo são listadas
algumas coleções disponíveis no serviço do *Brazil Data Cube* e suas
respectivas descrições, como exemplos:

-  MOD13Q1-6: Terra Moderate Resolution Imaging Spectroradiometer
   (MODIS) Vegetation Indices (MOD13Q1) Version 6.

-  S2_MSI_L2_SR_LASRC-1: Sentinel-2 SR - LaSRC/Fmask 4.2.

-  CB4_64-1: CBERS-4 - AWFI - Cube Identity - v001.

Bounding Box
^^^^^^^^^^^^

Um bbox representa uma área definida por duas longitudes e duas
latitudes, onde:

-  A latitude é um número decimal entre -90.0 e 90.0

-  A longitude é um número decimal entre -180.0 e 180.0

**Observação:** O formato segue o padrão: bbox = [min Longitude , min
Latitude , max Longitude , max Latitude]. As coordenadas acima podem ser
adiquiridas utilizando a ferramenta *online* para visualização dos
cubos, o `Portal do Projeto Brazil Data
Cube <http://brazildatacube.dpi.inpe.br/portal/explore>`__.

Filtros de entrada
^^^^^^^^^^^^^^^^^^

Para fins de testagem utilizaremos os seguintes parâmetros:

-  **Collection**: CBERS-4 - AWFI - Cube Stack 16 days - v001;
-  **Bands**: Red, Green, Blue e NIR (Near Infra-red);
-  **Bounding Box**: -46.1425924, -23.0466003, -45.5534169, -23.4302733;
-  **Start Date**: 2018-01-01;
-  **Last Date**: 2021-01-01.

Para este primeiro estudo de caso utilizaremos uma área de estudo
referente ao município de São José dos Campos.

Podemos conferir se estes atributos estão de acordo com a resposta
retornada acima e com os filtro definidos vamos conferir a documentação
para a biblioteca ``DataCube``:

.. code:: ipython3

    DataCube?

Com o retorno podemos verifirar a colocação e a nomeclatura das
variavéis e criar nosso cubo de dados de exemplo com base nesta
informação:

.. code:: ipython3

    %%time
    eodatacube = DataCube(
        collections=["CB4_64_16D_STK-1"],
        query_bands=['red', 'green', 'blue', 'nir'],
        bbox=[-46.1425924, -23.0466003, -45.5534169, -23.4302733],
        start_date="2018-01-01",
        end_date="2021-01-01",
        limit=50
    )


.. parsed-literal::

    CPU times: user 194 ms, sys: 57.5 ms, total: 252 ms
    Wall time: 5.03 s


Operações com o Cubo de dados
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Primeiramente com o cubo de dados criado podemos executar os métodos
listados anteriormente na documentação da biblioteca.

Vamos primeiro visualizar os dados adiquiridos em forma de imagems em
composição colorida.

Para este método é essencial a existência das bandas *Red*, *Green* e
*Blue* para o cálculo da composição colorida da imagem, caso estas
bandas não estejam na busca acarretará em um erro ou *Exception*.

Podemos visualizar qualquer uma das bandas selecionadas ou calcular os
índices espectrais cujo cálculo possua as bandas selecionadas como na
imagem a seguir:

.. code:: ipython3

    eodatacube.interactPlot("rgb") # "ndvi", "ndwi" ou qualquer outra banda selecionada

O método ``interactPlot`` retorna uma visualização interativa para o
``jupyter notebook``.

.. image:: ./assets/img/interact_plot.png

Podemos também visualizar uma banda em uma data específica para fins de
amostragem.

Por exemplo, queremos visualizar a banda espectral *Near Infra Red -
NIR* na data de 21 de Agosto de 2020.

Para isso formatamos a data e selecionamos uma banda, mais uma vez vamos
visualizar a documentação de um método, o ``DataCube.search`` que fará a
busca na base de dados completa.

.. code:: ipython3

    DataCube.search?

Com esta resposta podemos definir nossas variáveis.

.. code:: ipython3

    nir = eodatacube.search(band="nir",time="2020-08-21")
    nir




.. raw:: html

    <div><svg style="position: absolute; width: 0; height: 0; overflow: hidden">
    <defs>
    <symbol id="icon-database" viewBox="0 0 32 32">
    <path d="M16 0c-8.837 0-16 2.239-16 5v4c0 2.761 7.163 5 16 5s16-2.239 16-5v-4c0-2.761-7.163-5-16-5z"></path>
    <path d="M16 17c-8.837 0-16-2.239-16-5v6c0 2.761 7.163 5 16 5s16-2.239 16-5v-6c0 2.761-7.163 5-16 5z"></path>
    <path d="M16 26c-8.837 0-16-2.239-16-5v6c0 2.761 7.163 5 16 5s16-2.239 16-5v-6c0 2.761-7.163 5-16 5z"></path>
    </symbol>
    <symbol id="icon-file-text2" viewBox="0 0 32 32">
    <path d="M28.681 7.159c-0.694-0.947-1.662-2.053-2.724-3.116s-2.169-2.030-3.116-2.724c-1.612-1.182-2.393-1.319-2.841-1.319h-15.5c-1.378 0-2.5 1.121-2.5 2.5v27c0 1.378 1.122 2.5 2.5 2.5h23c1.378 0 2.5-1.122 2.5-2.5v-19.5c0-0.448-0.137-1.23-1.319-2.841zM24.543 5.457c0.959 0.959 1.712 1.825 2.268 2.543h-4.811v-4.811c0.718 0.556 1.584 1.309 2.543 2.268zM28 29.5c0 0.271-0.229 0.5-0.5 0.5h-23c-0.271 0-0.5-0.229-0.5-0.5v-27c0-0.271 0.229-0.5 0.5-0.5 0 0 15.499-0 15.5 0v7c0 0.552 0.448 1 1 1h7v19.5z"></path>
    <path d="M23 26h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
    <path d="M23 22h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
    <path d="M23 18h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
    </symbol>
    </defs>
    </svg>
    <style>/* CSS stylesheet for displaying xarray objects in jupyterlab.
     *
     */
    
    :root {
      --xr-font-color0: var(--jp-content-font-color0, rgba(0, 0, 0, 1));
      --xr-font-color2: var(--jp-content-font-color2, rgba(0, 0, 0, 0.54));
      --xr-font-color3: var(--jp-content-font-color3, rgba(0, 0, 0, 0.38));
      --xr-border-color: var(--jp-border-color2, #e0e0e0);
      --xr-disabled-color: var(--jp-layout-color3, #bdbdbd);
      --xr-background-color: var(--jp-layout-color0, white);
      --xr-background-color-row-even: var(--jp-layout-color1, white);
      --xr-background-color-row-odd: var(--jp-layout-color2, #eeeeee);
    }
    
    html[theme=dark],
    body.vscode-dark {
      --xr-font-color0: rgba(255, 255, 255, 1);
      --xr-font-color2: rgba(255, 255, 255, 0.54);
      --xr-font-color3: rgba(255, 255, 255, 0.38);
      --xr-border-color: #1F1F1F;
      --xr-disabled-color: #515151;
      --xr-background-color: #111111;
      --xr-background-color-row-even: #111111;
      --xr-background-color-row-odd: #313131;
    }
    
    .xr-wrap {
      display: block;
      min-width: 300px;
      max-width: 700px;
    }
    
    .xr-text-repr-fallback {
      /* fallback to plain text repr when CSS is not injected (untrusted notebook) */
      display: none;
    }
    
    .xr-header {
      padding-top: 6px;
      padding-bottom: 6px;
      margin-bottom: 4px;
      border-bottom: solid 1px var(--xr-border-color);
    }
    
    .xr-header > div,
    .xr-header > ul {
      display: inline;
      margin-top: 0;
      margin-bottom: 0;
    }
    
    .xr-obj-type,
    .xr-array-name {
      margin-left: 2px;
      margin-right: 10px;
    }
    
    .xr-obj-type {
      color: var(--xr-font-color2);
    }
    
    .xr-sections {
      padding-left: 0 !important;
      display: grid;
      grid-template-columns: 150px auto auto 1fr 20px 20px;
    }
    
    .xr-section-item {
      display: contents;
    }
    
    .xr-section-item input {
      display: none;
    }
    
    .xr-section-item input + label {
      color: var(--xr-disabled-color);
    }
    
    .xr-section-item input:enabled + label {
      cursor: pointer;
      color: var(--xr-font-color2);
    }
    
    .xr-section-item input:enabled + label:hover {
      color: var(--xr-font-color0);
    }
    
    .xr-section-summary {
      grid-column: 1;
      color: var(--xr-font-color2);
      font-weight: 500;
    }
    
    .xr-section-summary > span {
      display: inline-block;
      padding-left: 0.5em;
    }
    
    .xr-section-summary-in:disabled + label {
      color: var(--xr-font-color2);
    }
    
    .xr-section-summary-in + label:before {
      display: inline-block;
      content: '►';
      font-size: 11px;
      width: 15px;
      text-align: center;
    }
    
    .xr-section-summary-in:disabled + label:before {
      color: var(--xr-disabled-color);
    }
    
    .xr-section-summary-in:checked + label:before {
      content: '▼';
    }
    
    .xr-section-summary-in:checked + label > span {
      display: none;
    }
    
    .xr-section-summary,
    .xr-section-inline-details {
      padding-top: 4px;
      padding-bottom: 4px;
    }
    
    .xr-section-inline-details {
      grid-column: 2 / -1;
    }
    
    .xr-section-details {
      display: none;
      grid-column: 1 / -1;
      margin-bottom: 5px;
    }
    
    .xr-section-summary-in:checked ~ .xr-section-details {
      display: contents;
    }
    
    .xr-array-wrap {
      grid-column: 1 / -1;
      display: grid;
      grid-template-columns: 20px auto;
    }
    
    .xr-array-wrap > label {
      grid-column: 1;
      vertical-align: top;
    }
    
    .xr-preview {
      color: var(--xr-font-color3);
    }
    
    .xr-array-preview,
    .xr-array-data {
      padding: 0 5px !important;
      grid-column: 2;
    }
    
    .xr-array-data,
    .xr-array-in:checked ~ .xr-array-preview {
      display: none;
    }
    
    .xr-array-in:checked ~ .xr-array-data,
    .xr-array-preview {
      display: inline-block;
    }
    
    .xr-dim-list {
      display: inline-block !important;
      list-style: none;
      padding: 0 !important;
      margin: 0;
    }
    
    .xr-dim-list li {
      display: inline-block;
      padding: 0;
      margin: 0;
    }
    
    .xr-dim-list:before {
      content: '(';
    }
    
    .xr-dim-list:after {
      content: ')';
    }
    
    .xr-dim-list li:not(:last-child):after {
      content: ',';
      padding-right: 5px;
    }
    
    .xr-has-index {
      font-weight: bold;
    }
    
    .xr-var-list,
    .xr-var-item {
      display: contents;
    }
    
    .xr-var-item > div,
    .xr-var-item label,
    .xr-var-item > .xr-var-name span {
      background-color: var(--xr-background-color-row-even);
      margin-bottom: 0;
    }
    
    .xr-var-item > .xr-var-name:hover span {
      padding-right: 5px;
    }
    
    .xr-var-list > li:nth-child(odd) > div,
    .xr-var-list > li:nth-child(odd) > label,
    .xr-var-list > li:nth-child(odd) > .xr-var-name span {
      background-color: var(--xr-background-color-row-odd);
    }
    
    .xr-var-name {
      grid-column: 1;
    }
    
    .xr-var-dims {
      grid-column: 2;
    }
    
    .xr-var-dtype {
      grid-column: 3;
      text-align: right;
      color: var(--xr-font-color2);
    }
    
    .xr-var-preview {
      grid-column: 4;
    }
    
    .xr-var-name,
    .xr-var-dims,
    .xr-var-dtype,
    .xr-preview,
    .xr-attrs dt {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      padding-right: 10px;
    }
    
    .xr-var-name:hover,
    .xr-var-dims:hover,
    .xr-var-dtype:hover,
    .xr-attrs dt:hover {
      overflow: visible;
      width: auto;
      z-index: 1;
    }
    
    .xr-var-attrs,
    .xr-var-data {
      display: none;
      background-color: var(--xr-background-color) !important;
      padding-bottom: 5px !important;
    }
    
    .xr-var-attrs-in:checked ~ .xr-var-attrs,
    .xr-var-data-in:checked ~ .xr-var-data {
      display: block;
    }
    
    .xr-var-data > table {
      float: right;
    }
    
    .xr-var-name span,
    .xr-var-data,
    .xr-attrs {
      padding-left: 25px !important;
    }
    
    .xr-attrs,
    .xr-var-attrs,
    .xr-var-data {
      grid-column: 1 / -1;
    }
    
    dl.xr-attrs {
      padding: 0;
      margin: 0;
      display: grid;
      grid-template-columns: 125px auto;
    }
    
    .xr-attrs dt,
    .xr-attrs dd {
      padding: 0;
      margin: 0;
      float: left;
      padding-right: 10px;
      width: auto;
    }
    
    .xr-attrs dt {
      font-weight: normal;
      grid-column: 1;
    }
    
    .xr-attrs dt:hover span {
      display: inline-block;
      background: var(--xr-background-color);
      padding-right: 10px;
    }
    
    .xr-attrs dd {
      grid-column: 2;
      white-space: pre-wrap;
      word-break: break-all;
    }
    
    .xr-icon-database,
    .xr-icon-file-text2 {
      display: inline-block;
      vertical-align: middle;
      width: 1em;
      height: 1.5em !important;
      stroke-width: 0;
      stroke: currentColor;
      fill: currentColor;
    }
    </style><pre class='xr-text-repr-fallback'>&lt;xarray.DataArray [&#x27;ResultSearch_nir&#x27;] (time: 1, y: 633, x: 964)&gt;
    array([[[2549, 2582, 2430, ..., 2583, 2783, 2815],
            [2550, 2737, 2603, ..., 2578, 2918, 2953],
            [2677, 2898, 2844, ..., 2623, 2964, 3003],
            ...,
            [3102, 3049, 3114, ..., 2669, 2718, 2278],
            [3100, 3058, 3047, ..., 2772, 2761, 2623],
            [2839, 2791, 2783, ..., 2813, 2664, 2593]]], dtype=int16)
    Coordinates:
      * time     (time) datetime64[ns] 2020-08-28
      * y        (y) int64 0 1 2 3 4 5 6 7 8 ... 624 625 626 627 628 629 630 631 632
      * x        (x) int64 0 1 2 3 4 5 6 7 8 ... 955 956 957 958 959 960 961 962 963
    Attributes:
        CB4_64_16D_STK-1:  CBERS-4 - AWFI - Cube Stack 16 days - v001</pre><div class='xr-wrap' hidden><div class='xr-header'><div class='xr-obj-type'>xarray.DataArray</div><div class='xr-array-name'>'['ResultSearch_nir']'</div><ul class='xr-dim-list'><li><span class='xr-has-index'>time</span>: 1</li><li><span class='xr-has-index'>y</span>: 633</li><li><span class='xr-has-index'>x</span>: 964</li></ul></div><ul class='xr-sections'><li class='xr-section-item'><div class='xr-array-wrap'><input id='section-66993c61-edcb-4bcf-aba3-60dc9a839ece' class='xr-array-in' type='checkbox' checked><label for='section-66993c61-edcb-4bcf-aba3-60dc9a839ece' title='Show/hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-array-preview xr-preview'><span>2549 2582 2430 2471 2578 2689 2624 ... 2749 3191 3222 2813 2664 2593</span></div><div class='xr-array-data'><pre>array([[[2549, 2582, 2430, ..., 2583, 2783, 2815],
            [2550, 2737, 2603, ..., 2578, 2918, 2953],
            [2677, 2898, 2844, ..., 2623, 2964, 3003],
            ...,
            [3102, 3049, 3114, ..., 2669, 2718, 2278],
            [3100, 3058, 3047, ..., 2772, 2761, 2623],
            [2839, 2791, 2783, ..., 2813, 2664, 2593]]], dtype=int16)</pre></div></div></li><li class='xr-section-item'><input id='section-62d8077e-f063-4487-a9df-9da30025356c' class='xr-section-summary-in' type='checkbox'  checked><label for='section-62d8077e-f063-4487-a9df-9da30025356c' class='xr-section-summary' >Coordinates: <span>(3)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><ul class='xr-var-list'><li class='xr-var-item'><div class='xr-var-name'><span class='xr-has-index'>time</span></div><div class='xr-var-dims'>(time)</div><div class='xr-var-dtype'>datetime64[ns]</div><div class='xr-var-preview xr-preview'>2020-08-28</div><input id='attrs-ba8a4f90-7439-4a93-b393-2c49f3d6ecb0' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-ba8a4f90-7439-4a93-b393-2c49f3d6ecb0' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-fe81f6bb-dce0-4c6a-b89e-817010a66161' class='xr-var-data-in' type='checkbox'><label for='data-fe81f6bb-dce0-4c6a-b89e-817010a66161' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([&#x27;2020-08-28T00:00:00.000000000&#x27;], dtype=&#x27;datetime64[ns]&#x27;)</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span class='xr-has-index'>y</span></div><div class='xr-var-dims'>(y)</div><div class='xr-var-dtype'>int64</div><div class='xr-var-preview xr-preview'>0 1 2 3 4 5 ... 628 629 630 631 632</div><input id='attrs-d4efd936-1c94-42cb-a5a8-7f894b03c249' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-d4efd936-1c94-42cb-a5a8-7f894b03c249' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-e0b0829c-c8af-4736-ab7c-921b3817d642' class='xr-var-data-in' type='checkbox'><label for='data-e0b0829c-c8af-4736-ab7c-921b3817d642' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([  0,   1,   2, ..., 630, 631, 632])</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span class='xr-has-index'>x</span></div><div class='xr-var-dims'>(x)</div><div class='xr-var-dtype'>int64</div><div class='xr-var-preview xr-preview'>0 1 2 3 4 5 ... 959 960 961 962 963</div><input id='attrs-cbf0c1d8-73b1-4d37-9a3b-17cf8d0eb378' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-cbf0c1d8-73b1-4d37-9a3b-17cf8d0eb378' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-8b4f789e-1c21-48bd-9ba7-fae83faf8604' class='xr-var-data-in' type='checkbox'><label for='data-8b4f789e-1c21-48bd-9ba7-fae83faf8604' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([  0,   1,   2, ..., 961, 962, 963])</pre></div></li></ul></div></li><li class='xr-section-item'><input id='section-a4e0b7eb-517b-4cf9-90b4-5171c08fc3d1' class='xr-section-summary-in' type='checkbox'  checked><label for='section-a4e0b7eb-517b-4cf9-90b4-5171c08fc3d1' class='xr-section-summary' >Attributes: <span>(1)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><dl class='xr-attrs'><dt><span>CB4_64_16D_STK-1 :</span></dt><dd>CBERS-4 - AWFI - Cube Stack 16 days - v001</dd></dl></div></li></ul></div></div>



Com esta resposta podemos visualizar a imagem de forma customizada

.. code:: ipython3

    plt.figure(figsize=(10, 5))
    colormap = plt.get_cmap('Reds', 1000)
    plt.imshow(
        nir.values[0],
        cmap=colormap
    )
    plt.tight_layout()
    plt.colorbar()
    
    plt.show()



.. image:: ./assets/img/output_17_0.png


Geração de Índices Espectrais
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  Os índices espectrais são uma importante ferramenta da área de
   sensoriamento remoto.

-  Os índices espectrais possibilitam identificar diferentes alvos em
   imagens de satélites.

-  Neste trabalho, foi implementado um módulo que permite o cálculo dos
   índices espectrais: NDVI, NDWI e NDBI.

-  O objetivo é permitir que o usuário possa extrair informações
   desejadas, por meio do cálculo dos índices, a partir de matrizes de
   pixels das bandas.

-  **O que é o NDVI?**

O Índice de Vegetação de Diferença Normalizada (NDVI) é um indicador da
biomassa fotossinteticamente ativa. Consiste em um cálculo realizado por
meio de bandas espectrais que tem como objetivo indicar a saúde da
vegetação.

-  **O que o NDVI possibilita?**

O NDVI ajuda a diferenciar a vegetação de outros tipos de cobertura da
terra (como alvos não-naturais) e sua condição geral, bem como
identificar e classificar áreas cultivadas em mapas temáticos,
auxiliando na detecção de mudanças em padrões.

-  **Como o NDVI é calculado?**

O NDVI é calculado por meio da diferença entre a reflectância das bandas
infravermelho próximo (NIR) e do vermelho (RED), dividida pela soma das
duas reflectâncias, sendo expresso matematicamente como:

:math:`NDVI = \frac{NIR - RED}{NIR + RED}`

Para geração dos índices espectrais (NDVI, NDWI e NDBI) foi construído
um módulo, chamado indices.py. Este módulo contém as seguintes funções:

-  **calculo_ndvi(nir, red, cte_delta=1e-10)**

-  **calculo_ndwi(nir, green, cte_delta=1e-10)**

-  **calculo_ndbi(nir, swir1, cte_delta=1e-10)**

Uma constante foi criada para fazer uma adição no denominador de ambos
os cálculos dos índices espectrais. Por padrão, esta constante foi
definida com o valor de :math:`1e-10`. Caso o usuário desejar, poderá
alterar o valor da constante.

Podemos também visualizar os índices espectrais como NDVI, NDWI e NDBI
de uma data específica.

.. code:: ipython3

    ndvi = eodatacube.calculateNDVI("2020-08-21")
    ndvi




.. raw:: html

    <div><svg style="position: absolute; width: 0; height: 0; overflow: hidden">
    <defs>
    <symbol id="icon-database" viewBox="0 0 32 32">
    <path d="M16 0c-8.837 0-16 2.239-16 5v4c0 2.761 7.163 5 16 5s16-2.239 16-5v-4c0-2.761-7.163-5-16-5z"></path>
    <path d="M16 17c-8.837 0-16-2.239-16-5v6c0 2.761 7.163 5 16 5s16-2.239 16-5v-6c0 2.761-7.163 5-16 5z"></path>
    <path d="M16 26c-8.837 0-16-2.239-16-5v6c0 2.761 7.163 5 16 5s16-2.239 16-5v-6c0 2.761-7.163 5-16 5z"></path>
    </symbol>
    <symbol id="icon-file-text2" viewBox="0 0 32 32">
    <path d="M28.681 7.159c-0.694-0.947-1.662-2.053-2.724-3.116s-2.169-2.030-3.116-2.724c-1.612-1.182-2.393-1.319-2.841-1.319h-15.5c-1.378 0-2.5 1.121-2.5 2.5v27c0 1.378 1.122 2.5 2.5 2.5h23c1.378 0 2.5-1.122 2.5-2.5v-19.5c0-0.448-0.137-1.23-1.319-2.841zM24.543 5.457c0.959 0.959 1.712 1.825 2.268 2.543h-4.811v-4.811c0.718 0.556 1.584 1.309 2.543 2.268zM28 29.5c0 0.271-0.229 0.5-0.5 0.5h-23c-0.271 0-0.5-0.229-0.5-0.5v-27c0-0.271 0.229-0.5 0.5-0.5 0 0 15.499-0 15.5 0v7c0 0.552 0.448 1 1 1h7v19.5z"></path>
    <path d="M23 26h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
    <path d="M23 22h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
    <path d="M23 18h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
    </symbol>
    </defs>
    </svg>
    <style>/* CSS stylesheet for displaying xarray objects in jupyterlab.
     *
     */
    
    :root {
      --xr-font-color0: var(--jp-content-font-color0, rgba(0, 0, 0, 1));
      --xr-font-color2: var(--jp-content-font-color2, rgba(0, 0, 0, 0.54));
      --xr-font-color3: var(--jp-content-font-color3, rgba(0, 0, 0, 0.38));
      --xr-border-color: var(--jp-border-color2, #e0e0e0);
      --xr-disabled-color: var(--jp-layout-color3, #bdbdbd);
      --xr-background-color: var(--jp-layout-color0, white);
      --xr-background-color-row-even: var(--jp-layout-color1, white);
      --xr-background-color-row-odd: var(--jp-layout-color2, #eeeeee);
    }
    
    html[theme=dark],
    body.vscode-dark {
      --xr-font-color0: rgba(255, 255, 255, 1);
      --xr-font-color2: rgba(255, 255, 255, 0.54);
      --xr-font-color3: rgba(255, 255, 255, 0.38);
      --xr-border-color: #1F1F1F;
      --xr-disabled-color: #515151;
      --xr-background-color: #111111;
      --xr-background-color-row-even: #111111;
      --xr-background-color-row-odd: #313131;
    }
    
    .xr-wrap {
      display: block;
      min-width: 300px;
      max-width: 700px;
    }
    
    .xr-text-repr-fallback {
      /* fallback to plain text repr when CSS is not injected (untrusted notebook) */
      display: none;
    }
    
    .xr-header {
      padding-top: 6px;
      padding-bottom: 6px;
      margin-bottom: 4px;
      border-bottom: solid 1px var(--xr-border-color);
    }
    
    .xr-header > div,
    .xr-header > ul {
      display: inline;
      margin-top: 0;
      margin-bottom: 0;
    }
    
    .xr-obj-type,
    .xr-array-name {
      margin-left: 2px;
      margin-right: 10px;
    }
    
    .xr-obj-type {
      color: var(--xr-font-color2);
    }
    
    .xr-sections {
      padding-left: 0 !important;
      display: grid;
      grid-template-columns: 150px auto auto 1fr 20px 20px;
    }
    
    .xr-section-item {
      display: contents;
    }
    
    .xr-section-item input {
      display: none;
    }
    
    .xr-section-item input + label {
      color: var(--xr-disabled-color);
    }
    
    .xr-section-item input:enabled + label {
      cursor: pointer;
      color: var(--xr-font-color2);
    }
    
    .xr-section-item input:enabled + label:hover {
      color: var(--xr-font-color0);
    }
    
    .xr-section-summary {
      grid-column: 1;
      color: var(--xr-font-color2);
      font-weight: 500;
    }
    
    .xr-section-summary > span {
      display: inline-block;
      padding-left: 0.5em;
    }
    
    .xr-section-summary-in:disabled + label {
      color: var(--xr-font-color2);
    }
    
    .xr-section-summary-in + label:before {
      display: inline-block;
      content: '►';
      font-size: 11px;
      width: 15px;
      text-align: center;
    }
    
    .xr-section-summary-in:disabled + label:before {
      color: var(--xr-disabled-color);
    }
    
    .xr-section-summary-in:checked + label:before {
      content: '▼';
    }
    
    .xr-section-summary-in:checked + label > span {
      display: none;
    }
    
    .xr-section-summary,
    .xr-section-inline-details {
      padding-top: 4px;
      padding-bottom: 4px;
    }
    
    .xr-section-inline-details {
      grid-column: 2 / -1;
    }
    
    .xr-section-details {
      display: none;
      grid-column: 1 / -1;
      margin-bottom: 5px;
    }
    
    .xr-section-summary-in:checked ~ .xr-section-details {
      display: contents;
    }
    
    .xr-array-wrap {
      grid-column: 1 / -1;
      display: grid;
      grid-template-columns: 20px auto;
    }
    
    .xr-array-wrap > label {
      grid-column: 1;
      vertical-align: top;
    }
    
    .xr-preview {
      color: var(--xr-font-color3);
    }
    
    .xr-array-preview,
    .xr-array-data {
      padding: 0 5px !important;
      grid-column: 2;
    }
    
    .xr-array-data,
    .xr-array-in:checked ~ .xr-array-preview {
      display: none;
    }
    
    .xr-array-in:checked ~ .xr-array-data,
    .xr-array-preview {
      display: inline-block;
    }
    
    .xr-dim-list {
      display: inline-block !important;
      list-style: none;
      padding: 0 !important;
      margin: 0;
    }
    
    .xr-dim-list li {
      display: inline-block;
      padding: 0;
      margin: 0;
    }
    
    .xr-dim-list:before {
      content: '(';
    }
    
    .xr-dim-list:after {
      content: ')';
    }
    
    .xr-dim-list li:not(:last-child):after {
      content: ',';
      padding-right: 5px;
    }
    
    .xr-has-index {
      font-weight: bold;
    }
    
    .xr-var-list,
    .xr-var-item {
      display: contents;
    }
    
    .xr-var-item > div,
    .xr-var-item label,
    .xr-var-item > .xr-var-name span {
      background-color: var(--xr-background-color-row-even);
      margin-bottom: 0;
    }
    
    .xr-var-item > .xr-var-name:hover span {
      padding-right: 5px;
    }
    
    .xr-var-list > li:nth-child(odd) > div,
    .xr-var-list > li:nth-child(odd) > label,
    .xr-var-list > li:nth-child(odd) > .xr-var-name span {
      background-color: var(--xr-background-color-row-odd);
    }
    
    .xr-var-name {
      grid-column: 1;
    }
    
    .xr-var-dims {
      grid-column: 2;
    }
    
    .xr-var-dtype {
      grid-column: 3;
      text-align: right;
      color: var(--xr-font-color2);
    }
    
    .xr-var-preview {
      grid-column: 4;
    }
    
    .xr-var-name,
    .xr-var-dims,
    .xr-var-dtype,
    .xr-preview,
    .xr-attrs dt {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      padding-right: 10px;
    }
    
    .xr-var-name:hover,
    .xr-var-dims:hover,
    .xr-var-dtype:hover,
    .xr-attrs dt:hover {
      overflow: visible;
      width: auto;
      z-index: 1;
    }
    
    .xr-var-attrs,
    .xr-var-data {
      display: none;
      background-color: var(--xr-background-color) !important;
      padding-bottom: 5px !important;
    }
    
    .xr-var-attrs-in:checked ~ .xr-var-attrs,
    .xr-var-data-in:checked ~ .xr-var-data {
      display: block;
    }
    
    .xr-var-data > table {
      float: right;
    }
    
    .xr-var-name span,
    .xr-var-data,
    .xr-attrs {
      padding-left: 25px !important;
    }
    
    .xr-attrs,
    .xr-var-attrs,
    .xr-var-data {
      grid-column: 1 / -1;
    }
    
    dl.xr-attrs {
      padding: 0;
      margin: 0;
      display: grid;
      grid-template-columns: 125px auto;
    }
    
    .xr-attrs dt,
    .xr-attrs dd {
      padding: 0;
      margin: 0;
      float: left;
      padding-right: 10px;
      width: auto;
    }
    
    .xr-attrs dt {
      font-weight: normal;
      grid-column: 1;
    }
    
    .xr-attrs dt:hover span {
      display: inline-block;
      background: var(--xr-background-color);
      padding-right: 10px;
    }
    
    .xr-attrs dd {
      grid-column: 2;
      white-space: pre-wrap;
      word-break: break-all;
    }
    
    .xr-icon-database,
    .xr-icon-file-text2 {
      display: inline-block;
      vertical-align: middle;
      width: 1em;
      height: 1.5em !important;
      stroke-width: 0;
      stroke: currentColor;
      fill: currentColor;
    }
    </style><pre class='xr-text-repr-fallback'>&lt;xarray.DataArray [&#x27;ImageNDVI&#x27;] (time: 1, y: 633, x: 964)&gt;
    array([[[0.69537745, 0.76125512, 0.77891654, ..., 0.40380435,
             0.47717622, 0.54035568],
            [0.70113409, 0.68534483, 0.69908616, ..., 0.42509674,
             0.57815035, 0.61985738],
            [0.6964512 , 0.58101473, 0.55282555, ..., 0.3900371 ,
             0.55468135, 0.63651226],
            ...,
            [0.79565847, 0.80788615, 0.81257276, ..., 0.38757473,
             0.45114789, 0.3776837 ],
            [0.79970972, 0.8083974 , 0.80562963, ..., 0.40141557,
             0.44592825, 0.40870032],
            [0.79286391, 0.80588806, 0.79028627, ..., 0.4164149 ,
             0.39439937, 0.39784367]]])
    Coordinates:
      * time     (time) datetime64[ns] 2020-08-28
      * y        (y) int64 0 1 2 3 4 5 6 7 8 ... 624 625 626 627 628 629 630 631 632
      * x        (x) int64 0 1 2 3 4 5 6 7 8 ... 955 956 957 958 959 960 961 962 963
    Attributes:
        CB4_64_16D_STK-1:  CBERS-4 - AWFI - Cube Stack 16 days - v001</pre><div class='xr-wrap' hidden><div class='xr-header'><div class='xr-obj-type'>xarray.DataArray</div><div class='xr-array-name'>'['ImageNDVI']'</div><ul class='xr-dim-list'><li><span class='xr-has-index'>time</span>: 1</li><li><span class='xr-has-index'>y</span>: 633</li><li><span class='xr-has-index'>x</span>: 964</li></ul></div><ul class='xr-sections'><li class='xr-section-item'><div class='xr-array-wrap'><input id='section-4dbf5720-c14f-46f3-9ef7-c33a29cc40f5' class='xr-array-in' type='checkbox' checked><label for='section-4dbf5720-c14f-46f3-9ef7-c33a29cc40f5' title='Show/hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-array-preview xr-preview'><span>0.6954 0.7613 0.7789 0.7688 0.7585 ... 0.5435 0.4164 0.3944 0.3978</span></div><div class='xr-array-data'><pre>array([[[0.69537745, 0.76125512, 0.77891654, ..., 0.40380435,
             0.47717622, 0.54035568],
            [0.70113409, 0.68534483, 0.69908616, ..., 0.42509674,
             0.57815035, 0.61985738],
            [0.6964512 , 0.58101473, 0.55282555, ..., 0.3900371 ,
             0.55468135, 0.63651226],
            ...,
            [0.79565847, 0.80788615, 0.81257276, ..., 0.38757473,
             0.45114789, 0.3776837 ],
            [0.79970972, 0.8083974 , 0.80562963, ..., 0.40141557,
             0.44592825, 0.40870032],
            [0.79286391, 0.80588806, 0.79028627, ..., 0.4164149 ,
             0.39439937, 0.39784367]]])</pre></div></div></li><li class='xr-section-item'><input id='section-7b09a221-af86-43f1-9310-4b98f1484b64' class='xr-section-summary-in' type='checkbox'  checked><label for='section-7b09a221-af86-43f1-9310-4b98f1484b64' class='xr-section-summary' >Coordinates: <span>(3)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><ul class='xr-var-list'><li class='xr-var-item'><div class='xr-var-name'><span class='xr-has-index'>time</span></div><div class='xr-var-dims'>(time)</div><div class='xr-var-dtype'>datetime64[ns]</div><div class='xr-var-preview xr-preview'>2020-08-28</div><input id='attrs-0fd57b8c-d511-4262-bd5d-d309a022c054' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-0fd57b8c-d511-4262-bd5d-d309a022c054' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-e2acaf8b-6e45-4a73-a250-070ca1bd85d1' class='xr-var-data-in' type='checkbox'><label for='data-e2acaf8b-6e45-4a73-a250-070ca1bd85d1' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([&#x27;2020-08-28T00:00:00.000000000&#x27;], dtype=&#x27;datetime64[ns]&#x27;)</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span class='xr-has-index'>y</span></div><div class='xr-var-dims'>(y)</div><div class='xr-var-dtype'>int64</div><div class='xr-var-preview xr-preview'>0 1 2 3 4 5 ... 628 629 630 631 632</div><input id='attrs-fb0b964b-d252-4c02-ab5f-0f9589aedda7' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-fb0b964b-d252-4c02-ab5f-0f9589aedda7' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-f3c09588-98f5-4916-a3ce-07b11bc36f73' class='xr-var-data-in' type='checkbox'><label for='data-f3c09588-98f5-4916-a3ce-07b11bc36f73' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([  0,   1,   2, ..., 630, 631, 632])</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span class='xr-has-index'>x</span></div><div class='xr-var-dims'>(x)</div><div class='xr-var-dtype'>int64</div><div class='xr-var-preview xr-preview'>0 1 2 3 4 5 ... 959 960 961 962 963</div><input id='attrs-95b79330-8f66-4e50-92dd-6ab5f7c8aca7' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-95b79330-8f66-4e50-92dd-6ab5f7c8aca7' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-ce49a497-0157-4fc3-9042-408e00f9f1d0' class='xr-var-data-in' type='checkbox'><label for='data-ce49a497-0157-4fc3-9042-408e00f9f1d0' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([  0,   1,   2, ..., 961, 962, 963])</pre></div></li></ul></div></li><li class='xr-section-item'><input id='section-669a3bf4-c92f-44cb-83c5-30ef5f903b44' class='xr-section-summary-in' type='checkbox'  checked><label for='section-669a3bf4-c92f-44cb-83c5-30ef5f903b44' class='xr-section-summary' >Attributes: <span>(1)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><dl class='xr-attrs'><dt><span>CB4_64_16D_STK-1 :</span></dt><dd>CBERS-4 - AWFI - Cube Stack 16 days - v001</dd></dl></div></li></ul></div></div>



E mais uma vez podemos customizar a imagem em um plot em python.

.. code:: ipython3

    plt.figure(figsize=(10, 5))
    colormap = plt.get_cmap('Greens', 1000)
    plt.imshow(
        ndvi.values[0],
        cmap=colormap
    )
    plt.tight_layout()
    plt.colorbar()
    
    plt.show()



.. image:: ./assets/img/output_21_0.png


Séries temporais
^^^^^^^^^^^^^^^^

Por meio de um cubo de dados podemos visualizar uma série temporal com
base nas mudanças que um determinado ponto no mapa (na área de
interesse) sovreu durante um certo período de tempo.

Para este método também é possivel visualizar a documentação para
inferir um período de tempo customizado desde que se enquadre no período
de tempo selecionado.

Há um exemplo de uso abaixo:

.. code:: ipython3

    time_series = eodatacube.getTimeSeries(
        band='nir', lon=-45.7422561, lat=-23.2508317#, start_date="2020-01-01", end_date="2021-01-01"
    )
    time_series




.. raw:: html

    <div><svg style="position: absolute; width: 0; height: 0; overflow: hidden">
    <defs>
    <symbol id="icon-database" viewBox="0 0 32 32">
    <path d="M16 0c-8.837 0-16 2.239-16 5v4c0 2.761 7.163 5 16 5s16-2.239 16-5v-4c0-2.761-7.163-5-16-5z"></path>
    <path d="M16 17c-8.837 0-16-2.239-16-5v6c0 2.761 7.163 5 16 5s16-2.239 16-5v-6c0 2.761-7.163 5-16 5z"></path>
    <path d="M16 26c-8.837 0-16-2.239-16-5v6c0 2.761 7.163 5 16 5s16-2.239 16-5v-6c0 2.761-7.163 5-16 5z"></path>
    </symbol>
    <symbol id="icon-file-text2" viewBox="0 0 32 32">
    <path d="M28.681 7.159c-0.694-0.947-1.662-2.053-2.724-3.116s-2.169-2.030-3.116-2.724c-1.612-1.182-2.393-1.319-2.841-1.319h-15.5c-1.378 0-2.5 1.121-2.5 2.5v27c0 1.378 1.122 2.5 2.5 2.5h23c1.378 0 2.5-1.122 2.5-2.5v-19.5c0-0.448-0.137-1.23-1.319-2.841zM24.543 5.457c0.959 0.959 1.712 1.825 2.268 2.543h-4.811v-4.811c0.718 0.556 1.584 1.309 2.543 2.268zM28 29.5c0 0.271-0.229 0.5-0.5 0.5h-23c-0.271 0-0.5-0.229-0.5-0.5v-27c0-0.271 0.229-0.5 0.5-0.5 0 0 15.499-0 15.5 0v7c0 0.552 0.448 1 1 1h7v19.5z"></path>
    <path d="M23 26h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
    <path d="M23 22h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
    <path d="M23 18h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
    </symbol>
    </defs>
    </svg>
    <style>/* CSS stylesheet for displaying xarray objects in jupyterlab.
     *
     */
    
    :root {
      --xr-font-color0: var(--jp-content-font-color0, rgba(0, 0, 0, 1));
      --xr-font-color2: var(--jp-content-font-color2, rgba(0, 0, 0, 0.54));
      --xr-font-color3: var(--jp-content-font-color3, rgba(0, 0, 0, 0.38));
      --xr-border-color: var(--jp-border-color2, #e0e0e0);
      --xr-disabled-color: var(--jp-layout-color3, #bdbdbd);
      --xr-background-color: var(--jp-layout-color0, white);
      --xr-background-color-row-even: var(--jp-layout-color1, white);
      --xr-background-color-row-odd: var(--jp-layout-color2, #eeeeee);
    }
    
    html[theme=dark],
    body.vscode-dark {
      --xr-font-color0: rgba(255, 255, 255, 1);
      --xr-font-color2: rgba(255, 255, 255, 0.54);
      --xr-font-color3: rgba(255, 255, 255, 0.38);
      --xr-border-color: #1F1F1F;
      --xr-disabled-color: #515151;
      --xr-background-color: #111111;
      --xr-background-color-row-even: #111111;
      --xr-background-color-row-odd: #313131;
    }
    
    .xr-wrap {
      display: block;
      min-width: 300px;
      max-width: 700px;
    }
    
    .xr-text-repr-fallback {
      /* fallback to plain text repr when CSS is not injected (untrusted notebook) */
      display: none;
    }
    
    .xr-header {
      padding-top: 6px;
      padding-bottom: 6px;
      margin-bottom: 4px;
      border-bottom: solid 1px var(--xr-border-color);
    }
    
    .xr-header > div,
    .xr-header > ul {
      display: inline;
      margin-top: 0;
      margin-bottom: 0;
    }
    
    .xr-obj-type,
    .xr-array-name {
      margin-left: 2px;
      margin-right: 10px;
    }
    
    .xr-obj-type {
      color: var(--xr-font-color2);
    }
    
    .xr-sections {
      padding-left: 0 !important;
      display: grid;
      grid-template-columns: 150px auto auto 1fr 20px 20px;
    }
    
    .xr-section-item {
      display: contents;
    }
    
    .xr-section-item input {
      display: none;
    }
    
    .xr-section-item input + label {
      color: var(--xr-disabled-color);
    }
    
    .xr-section-item input:enabled + label {
      cursor: pointer;
      color: var(--xr-font-color2);
    }
    
    .xr-section-item input:enabled + label:hover {
      color: var(--xr-font-color0);
    }
    
    .xr-section-summary {
      grid-column: 1;
      color: var(--xr-font-color2);
      font-weight: 500;
    }
    
    .xr-section-summary > span {
      display: inline-block;
      padding-left: 0.5em;
    }
    
    .xr-section-summary-in:disabled + label {
      color: var(--xr-font-color2);
    }
    
    .xr-section-summary-in + label:before {
      display: inline-block;
      content: '►';
      font-size: 11px;
      width: 15px;
      text-align: center;
    }
    
    .xr-section-summary-in:disabled + label:before {
      color: var(--xr-disabled-color);
    }
    
    .xr-section-summary-in:checked + label:before {
      content: '▼';
    }
    
    .xr-section-summary-in:checked + label > span {
      display: none;
    }
    
    .xr-section-summary,
    .xr-section-inline-details {
      padding-top: 4px;
      padding-bottom: 4px;
    }
    
    .xr-section-inline-details {
      grid-column: 2 / -1;
    }
    
    .xr-section-details {
      display: none;
      grid-column: 1 / -1;
      margin-bottom: 5px;
    }
    
    .xr-section-summary-in:checked ~ .xr-section-details {
      display: contents;
    }
    
    .xr-array-wrap {
      grid-column: 1 / -1;
      display: grid;
      grid-template-columns: 20px auto;
    }
    
    .xr-array-wrap > label {
      grid-column: 1;
      vertical-align: top;
    }
    
    .xr-preview {
      color: var(--xr-font-color3);
    }
    
    .xr-array-preview,
    .xr-array-data {
      padding: 0 5px !important;
      grid-column: 2;
    }
    
    .xr-array-data,
    .xr-array-in:checked ~ .xr-array-preview {
      display: none;
    }
    
    .xr-array-in:checked ~ .xr-array-data,
    .xr-array-preview {
      display: inline-block;
    }
    
    .xr-dim-list {
      display: inline-block !important;
      list-style: none;
      padding: 0 !important;
      margin: 0;
    }
    
    .xr-dim-list li {
      display: inline-block;
      padding: 0;
      margin: 0;
    }
    
    .xr-dim-list:before {
      content: '(';
    }
    
    .xr-dim-list:after {
      content: ')';
    }
    
    .xr-dim-list li:not(:last-child):after {
      content: ',';
      padding-right: 5px;
    }
    
    .xr-has-index {
      font-weight: bold;
    }
    
    .xr-var-list,
    .xr-var-item {
      display: contents;
    }
    
    .xr-var-item > div,
    .xr-var-item label,
    .xr-var-item > .xr-var-name span {
      background-color: var(--xr-background-color-row-even);
      margin-bottom: 0;
    }
    
    .xr-var-item > .xr-var-name:hover span {
      padding-right: 5px;
    }
    
    .xr-var-list > li:nth-child(odd) > div,
    .xr-var-list > li:nth-child(odd) > label,
    .xr-var-list > li:nth-child(odd) > .xr-var-name span {
      background-color: var(--xr-background-color-row-odd);
    }
    
    .xr-var-name {
      grid-column: 1;
    }
    
    .xr-var-dims {
      grid-column: 2;
    }
    
    .xr-var-dtype {
      grid-column: 3;
      text-align: right;
      color: var(--xr-font-color2);
    }
    
    .xr-var-preview {
      grid-column: 4;
    }
    
    .xr-var-name,
    .xr-var-dims,
    .xr-var-dtype,
    .xr-preview,
    .xr-attrs dt {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      padding-right: 10px;
    }
    
    .xr-var-name:hover,
    .xr-var-dims:hover,
    .xr-var-dtype:hover,
    .xr-attrs dt:hover {
      overflow: visible;
      width: auto;
      z-index: 1;
    }
    
    .xr-var-attrs,
    .xr-var-data {
      display: none;
      background-color: var(--xr-background-color) !important;
      padding-bottom: 5px !important;
    }
    
    .xr-var-attrs-in:checked ~ .xr-var-attrs,
    .xr-var-data-in:checked ~ .xr-var-data {
      display: block;
    }
    
    .xr-var-data > table {
      float: right;
    }
    
    .xr-var-name span,
    .xr-var-data,
    .xr-attrs {
      padding-left: 25px !important;
    }
    
    .xr-attrs,
    .xr-var-attrs,
    .xr-var-data {
      grid-column: 1 / -1;
    }
    
    dl.xr-attrs {
      padding: 0;
      margin: 0;
      display: grid;
      grid-template-columns: 125px auto;
    }
    
    .xr-attrs dt,
    .xr-attrs dd {
      padding: 0;
      margin: 0;
      float: left;
      padding-right: 10px;
      width: auto;
    }
    
    .xr-attrs dt {
      font-weight: normal;
      grid-column: 1;
    }
    
    .xr-attrs dt:hover span {
      display: inline-block;
      background: var(--xr-background-color);
      padding-right: 10px;
    }
    
    .xr-attrs dd {
      grid-column: 2;
      white-space: pre-wrap;
      word-break: break-all;
    }
    
    .xr-icon-database,
    .xr-icon-file-text2 {
      display: inline-block;
      vertical-align: middle;
      width: 1em;
      height: 1.5em !important;
      stroke-width: 0;
      stroke: currentColor;
      fill: currentColor;
    }
    </style><pre class='xr-text-repr-fallback'>&lt;xarray.DataArray [&#x27;TimeSeries_NIR&#x27;] (time: 50)&gt;
    array([2972, 4007, 3721, 3540, 5045, 2043, 3164, 3745, 3283, 2029, 2899,
           3220, 2816, 2869, 1251, 2676, 2784, 2759, 2458, 3391, 2436, 2595,
           2759, 3398, 7836, 2856, 3462, 3306, 2889, 3311, 2960, 2957, 1536,
           1936, 3288, 2972, 2768, 2826, 3878, 3170, 2831, 2701, 2635, 2808,
           2873, 2858, 3984, 3990, 4060, 3945], dtype=int16)
    Coordinates:
      * time     (time) datetime64[ns] 2018-10-16 2018-11-01 ... 2021-01-01
    Attributes:
        longitude:  -45.7422561
        latitude:   -23.2508317</pre><div class='xr-wrap' hidden><div class='xr-header'><div class='xr-obj-type'>xarray.DataArray</div><div class='xr-array-name'>'['TimeSeries_NIR']'</div><ul class='xr-dim-list'><li><span class='xr-has-index'>time</span>: 50</li></ul></div><ul class='xr-sections'><li class='xr-section-item'><div class='xr-array-wrap'><input id='section-16cf8e12-45ae-485f-a4c6-e7c997c74929' class='xr-array-in' type='checkbox' checked><label for='section-16cf8e12-45ae-485f-a4c6-e7c997c74929' title='Show/hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-array-preview xr-preview'><span>2972 4007 3721 3540 5045 2043 3164 ... 2873 2858 3984 3990 4060 3945</span></div><div class='xr-array-data'><pre>array([2972, 4007, 3721, 3540, 5045, 2043, 3164, 3745, 3283, 2029, 2899,
           3220, 2816, 2869, 1251, 2676, 2784, 2759, 2458, 3391, 2436, 2595,
           2759, 3398, 7836, 2856, 3462, 3306, 2889, 3311, 2960, 2957, 1536,
           1936, 3288, 2972, 2768, 2826, 3878, 3170, 2831, 2701, 2635, 2808,
           2873, 2858, 3984, 3990, 4060, 3945], dtype=int16)</pre></div></div></li><li class='xr-section-item'><input id='section-5943a8bb-5dda-423c-b2ef-f662515a5b58' class='xr-section-summary-in' type='checkbox'  checked><label for='section-5943a8bb-5dda-423c-b2ef-f662515a5b58' class='xr-section-summary' >Coordinates: <span>(1)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><ul class='xr-var-list'><li class='xr-var-item'><div class='xr-var-name'><span class='xr-has-index'>time</span></div><div class='xr-var-dims'>(time)</div><div class='xr-var-dtype'>datetime64[ns]</div><div class='xr-var-preview xr-preview'>2018-10-16 ... 2021-01-01</div><input id='attrs-4ccb6fd7-26de-43ea-a5f3-37f936b46455' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-4ccb6fd7-26de-43ea-a5f3-37f936b46455' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-0030ab52-bcc8-44fd-ae89-ffad0fc79209' class='xr-var-data-in' type='checkbox'><label for='data-0030ab52-bcc8-44fd-ae89-ffad0fc79209' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([&#x27;2018-10-16T00:00:00.000000000&#x27;, &#x27;2018-11-01T00:00:00.000000000&#x27;,
           &#x27;2018-11-17T00:00:00.000000000&#x27;, &#x27;2018-12-03T00:00:00.000000000&#x27;,
           &#x27;2018-12-19T00:00:00.000000000&#x27;, &#x27;2019-01-01T00:00:00.000000000&#x27;,
           &#x27;2019-01-17T00:00:00.000000000&#x27;, &#x27;2019-02-02T00:00:00.000000000&#x27;,
           &#x27;2019-02-18T00:00:00.000000000&#x27;, &#x27;2019-03-06T00:00:00.000000000&#x27;,
           &#x27;2019-03-22T00:00:00.000000000&#x27;, &#x27;2019-04-07T00:00:00.000000000&#x27;,
           &#x27;2019-04-23T00:00:00.000000000&#x27;, &#x27;2019-05-09T00:00:00.000000000&#x27;,
           &#x27;2019-05-25T00:00:00.000000000&#x27;, &#x27;2019-06-10T00:00:00.000000000&#x27;,
           &#x27;2019-06-26T00:00:00.000000000&#x27;, &#x27;2019-07-12T00:00:00.000000000&#x27;,
           &#x27;2019-07-28T00:00:00.000000000&#x27;, &#x27;2019-08-13T00:00:00.000000000&#x27;,
           &#x27;2019-08-29T00:00:00.000000000&#x27;, &#x27;2019-09-14T00:00:00.000000000&#x27;,
           &#x27;2019-09-30T00:00:00.000000000&#x27;, &#x27;2019-10-16T00:00:00.000000000&#x27;,
           &#x27;2019-11-01T00:00:00.000000000&#x27;, &#x27;2019-11-17T00:00:00.000000000&#x27;,
           &#x27;2019-12-03T00:00:00.000000000&#x27;, &#x27;2019-12-19T00:00:00.000000000&#x27;,
           &#x27;2020-01-01T00:00:00.000000000&#x27;, &#x27;2020-01-17T00:00:00.000000000&#x27;,
           &#x27;2020-02-18T00:00:00.000000000&#x27;, &#x27;2020-03-05T00:00:00.000000000&#x27;,
           &#x27;2020-03-21T00:00:00.000000000&#x27;, &#x27;2020-04-06T00:00:00.000000000&#x27;,
           &#x27;2020-04-22T00:00:00.000000000&#x27;, &#x27;2020-05-08T00:00:00.000000000&#x27;,
           &#x27;2020-06-09T00:00:00.000000000&#x27;, &#x27;2020-06-25T00:00:00.000000000&#x27;,
           &#x27;2020-07-11T00:00:00.000000000&#x27;, &#x27;2020-07-27T00:00:00.000000000&#x27;,
           &#x27;2020-08-12T00:00:00.000000000&#x27;, &#x27;2020-08-28T00:00:00.000000000&#x27;,
           &#x27;2020-09-13T00:00:00.000000000&#x27;, &#x27;2020-09-29T00:00:00.000000000&#x27;,
           &#x27;2020-10-15T00:00:00.000000000&#x27;, &#x27;2020-10-31T00:00:00.000000000&#x27;,
           &#x27;2020-11-16T00:00:00.000000000&#x27;, &#x27;2020-12-02T00:00:00.000000000&#x27;,
           &#x27;2020-12-18T00:00:00.000000000&#x27;, &#x27;2021-01-01T00:00:00.000000000&#x27;],
          dtype=&#x27;datetime64[ns]&#x27;)</pre></div></li></ul></div></li><li class='xr-section-item'><input id='section-2fd06a13-2540-4b57-87eb-c62a69ac3df6' class='xr-section-summary-in' type='checkbox'  checked><label for='section-2fd06a13-2540-4b57-87eb-c62a69ac3df6' class='xr-section-summary' >Attributes: <span>(2)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><dl class='xr-attrs'><dt><span>longitude :</span></dt><dd>-45.7422561</dd><dt><span>latitude :</span></dt><dd>-23.2508317</dd></dl></div></li></ul></div></div>



Com este dado repurado podemos visualizar uma série temporal em gráfico
com o ``matplotlib`` conforme se segue:

.. code:: ipython3

    x = time_series.time
    y = time_series
    
    plt.figure(figsize=(10,5))
    plt.title(f"\nTime Series\n")
    plt.xlabel('Time')
    plt.ylabel('Near Infra Red')
    plt.plot(x, y, color="red", linewidth=2)
    plt.tight_layout()
    plt.grid()
    plt.show()



.. image:: ./assets/img/output_25_0.png


Estudo de Caso na Área de Proteção Ambiental do Planalto Central - Brasília
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Neste estudo de caso foi selecionada uma área onde houve incidência de
queimadas no período do mês de agosto em 2019 na Área de Proteção
Ambiental do Planalto a Central, localizado no Distrito Federal,
Brasília. Os filtros criados para este estudo de caso são mostrados nos
tópicos a seguir:

-  **Collection:** S2_10_16D_STK-1;
-  **Bands:** Red, Green, Blue e NIR (Near Infra-red);
-  **Bounding Box:** -47.9910, -15.9653, -47.9632, -15.9463;
-  **Start Date:** 2019-01-01;
-  **End Date:** 2019-01-01.

.. code:: ipython3

    %%time
    eocube_service = DataCube(
        collections=["S2_10_16D_STK-1"],
        query_bands=['red', 'green', 'blue', 'nir', 'ndvi'],
        bbox=[-47.9910,-15.9653,-47.9632,-15.9463],
        start_date="2019-01-01",
        end_date="2020-01-01",
        limit=50
    )
    eocube_service.interactPlot('rgb')



.. parsed-literal::

    interactive(children=(Dropdown(description='date', options=(datetime.datetime(2019, 1, 1, 0, 0), datetime.date…


.. parsed-literal::

    CPU times: user 578 ms, sys: 212 ms, total: 790 ms
    Wall time: 4.89 s


Com o pacote *EOCube* é permitido calcular alguns índices espectrais
como o NDVI para o município selecionado no dia 16 de agosto em 2018.

Com este índice é possível visualizar as áreas que apresentam maiores
índices de vegetação, e neste caso de uso pode-se observar a área
degradada pela queimada em duas datas diferentes para o mês de agosto de
2019.

.. code:: ipython3

    %%time
    ndvi = eocube_service.search('ndvi')
    
    loc1 = ndvi.loc['2019-08-13'].values
    loc2 = ndvi.loc['2019-08-29'].values
    
    plt.figure(figsize=(40, 10))
    plt.subplot(151)
    plt.imshow(loc1, cmap='Greens')
    plt.title('2019-08-13 - NDVI')
    plt.subplot(152)
    plt.imshow(loc2, cmap='Greens')
    plt.title('2019-08-29 - NDVI')


.. parsed-literal::

    CPU times: user 921 ms, sys: 34.2 ms, total: 955 ms
    Wall time: 4.58 s




.. parsed-literal::

    Text(0.5, 1.0, '2019-08-29 - NDVI')




.. image:: ./assets/img/output_29_2.png


A série temporal gerada abaixo foi baseada em um ponto, com coordenadas
-47.9886031 e -15.9533037, específico da imagem recuperada para o
cálculo dos índices para o período selecionado.

É possível observar que no mês de agosto aconteceu uma queda
considerável no valor de NDVI devido a degradação observada na figura
anterior.

.. code:: ipython3

    %%time
    ts = eocube_service.getTimeSeries(
        band='ndvi',
        lon=-47.9886031, lat= -15.9533037,
        start_date = "2019-01-01", end_date="2020-01-01"
    )
    
    x = ts.time.values
    y = ts.values/ts.values.max()
    
    plt.figure(figsize=(10,5))
    plt.title(f"\nTime Series\n")
    plt.xlabel('Time')
    plt.ylabel('NDVI')
    plt.ylim([0,1])
    plt.plot(x, y, color="green", linewidth=2)
    plt.tight_layout()
    plt.grid()
    plt.show()



.. image:: ./assets/img/output_31_0.png


.. parsed-literal::

    CPU times: user 1.57 s, sys: 247 ms, total: 1.81 s
    Wall time: 3.77 s


Conclusão
---------

Por fim, cabe ressaltar que o projeto de desenvolvimento do pacote
*EOCube* apresentado, permite à comunidade científica o acesso, a
recuperação e a visualização de dados de uso e cobertura da Terra.

Os estudos de caso apresentaram resultados satisfatórios em relação a
proposta do pacote pela criação de cubos de dados para áreas do
território brasileiro, realizando a análise através do tempo. Como
proposta para trabalhos futuros, as sugestões são aprimorar o pacote
*EOCube* por meio do desenvolvimento de novas funcionalidades como a
programação paralela e a estruturação dos dados.
