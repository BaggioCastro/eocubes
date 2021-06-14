..
    This file is part of Python Client Library for Earth Observation Data Cube.
    Copyright (C) 2021 None.

    Python Client Library for Earth Observation Data Cube is free software;
    You can redistribute it and/or modify it under the terms of the MIT License;
    See LICENSE file for more details.

==========
Instalação
==========

Requisitos necessários `Python version +3 <https://www.python.org/>`_.

Para instalar o pacote python para acessar dados de observação da terra faça o clone do repositório:

.. code-block:: shell

    git clone https://github.com/prog-geo/eocubes

Antes de instalar as dependências atualize para a versão mais recente do gerenciador de pacotes `python-pip`:

.. code-block:: shell

    pip install --upgrade pip

Instalação simples
------------------

Na pasta root do repositório `/eocubes` execute o comando abaixo para instalar o pacote juntamente com as dependências necessárias

.. code-block:: shell

    pip install -e .[all]

.. note::

    Caso houver algum problema na instalação por conta de uma
    dependência é recomendável a criação de um ambiente virtual `conda` ou `pyenv`.

Criação do Ambiente Virtual
---------------------------

A instalação por meio de um ambiente virtual pode ser feita utilizando a ferramenta `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ ou o pacote `pypenv <https://pypi.org/project/pyenv/>`_.

Miniconda
*********

Para criar um ambiente virtual com o `miniconda` execute o comando abaixo:

.. code-block:: shell

    conda create --name eocube python==3.8

Ative o ambiente virtual:

.. code-block:: shell

    conda activate eocube

Pyenv
*****

Para criar um ambiente virtual com o `pyenv` execute o comando abaixo:

.. code-block:: shell

    python3 -m venv venv

Ative o ambiente virtual:

.. code-block:: shell

    source venv/bin/activate

.. note::

    Com o ambiente virtual criado é possível executar os comandos de instalação do pacote:

    .. code-block:: shell

        python -m pip install -e .[all]
