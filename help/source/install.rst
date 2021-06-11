..
    This file is part of Python Client Library for Earth Observation Data Cube.
    Copyright (C) 2021 None.

    Python Client Library for Earth Observation Data Cube is free software;
    You can redistribute it and/or modify it under the terms of the MIT License;
    See LICENSE file for more details.

============
Installation
============

Criação do Ambiente Virtual MiniConda
-------------------------------------

Criar um ambiente com o miniconda:

.. code-block:: shell

    $ conda create --name eocube python==3.8

Ativar o ambiente:

.. code-block:: shell

    $ conda activate eocube

Instalando as dependências
--------------------------

Instalando a dependência `IPython` para utilizar o ambiente conda no jupyter:

.. code-block:: shell

    (eocube) $ conda install -c anaconda ipython ipykernel jupyter

Para instalar as dependências específicas de cada exemplo [EO Cube](./eocube) e o serviço [EO Cube](./eocube), faremos uma conexão com o ambiente virtual criado anteriormente:

.. code-block:: shell

    (eocube) $ ipython kernel install --user --name eocube

Documentação e Testes
---------------------

Construção da documentação e execução dos testes unitários para a API e o pacote EOCube `./help/build/index.html`.

.. code-block:: shell

    eocube) $ sudo chmod +x ./build.sh && ./build.sh

Execução
--------

Execução do pacote no ambiente Jupyter no Python.

.. code-block:: shell

    (eocube) $ jupyter-notebook

Instalação das Dependências
---------------------------

Atualizar o pacote `pip` e o `setuptools` para a instalação:

.. code-block:: shell

    (eocube) ~/eocube $ python -m pip install --upgrade pip setuptools

Realizar a instalação do pacote `GDAL` para a manipulação de imagens:

.. code-block:: shell

    (eocube) ~/eocube $ conda install GDAL

Instalar as depências utilizando o arquivo [`setup.py`](./setup.py):

.. code-block:: shell

    (eocube) ~/eocube $ python -m pip install -e .[all]

Execução
--------

 - **Obs.:** Não esqueça de que a cada atualização do pacote o comando de instalação `.[all]` deve ser executado para atualizar o repositório, o kernel do `jupyter-notebook` deve ser reiniciado também:

.. code-block:: python

    from eocube import EOCube
