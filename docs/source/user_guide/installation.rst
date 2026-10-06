============
Installation
============

This page goes through the steps for installing the required packages to use the GROMACS plugin for AiiDA.

Python Virtual Environment
--------------------------

We recommend setting up a Python virtual environment via Conda, which can be installed by downloading the relevant installer `here <https://docs.conda.io/en/latest/miniconda.html>`_.
If you're using Linux, install conda via the terminal with:

.. code-block:: bash

    bash Miniconda3-latest-Linux-x86_64.sh

Then add the conda path to the bash environment by appending the following to your ``.bashrc`` file:

.. code-block:: bash

    export PATH="~/miniconda3/bin:$PATH"

Installation
------------

Our AiiDA plugin has been tested with AiiDA ``v2.9.0`` to ``v2.9.1``, Python versions ``3.12`` to ``3.14``, GROMACS version ``2026.3`` and Plumed version ``2.10.1``. If you are using a linux OS, execute the following in the terminal, which installs AiiDA, aiida-gromacs, GROMACS and Plumed via a conda installation

.. code-block:: bash

    conda create --name aiida-gromacs-env -c conda-forge python=3.14 aiida-core=2.9.1 gromacs=2026.3=nompi_* plumed=2.10.1=mpi_nompi_*


That is it. You have completed all the installation steps to record simulation data provenance for GROMACS.


Alternative Installation of aiida-gromcas via Pip
-------------------------------------------------

To install the AiiDA-gromacs plugin via Pip, activate the conda environment created previously and install with:

.. code-block:: bash

    conda activate aiida-2.9.1
    pip install aiida-gromacs
