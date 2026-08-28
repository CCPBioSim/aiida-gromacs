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

Options for AiiDA Installation
------------------------------

Our AiiDA plugin has been tested with AiiDA ``v2.4.0`` to ``v2.6.1``, we recommend to `install <https://aiida.readthedocs.io/projects/aiida-core/en/v2.4.0/intro/install_conda.html#intro-get-started-conda-install>`_ one of these versions of AiiDA in a conda environment. If you are using a linux OS, execute the following in the terminal, which installs AiiDA via an initial mamba installation

.. code-block:: bash

    conda create --name aiida-2.4.0 -c conda-forge aiida-core=2.4.0 aiida-core.services=2.4.0 python=3.11.0

Plugin Installation
-------------------

To install the AiiDA-gromacs plugin, activate the conda environment created previously and install our plugin via Pip,

.. code-block:: bash

    conda activate aiida-2.9.1
    pip install aiida-gromacs

Alternative Installation via Conda
----------------------------------

The AiiDA-Gromacs plugin is also available via the CCPBioSim Anaconda channel.

To install using Conda:

.. code-block:: bash

    conda activate aiida-2.9.1
    conda install -c CCPBioSim aiida-gromacs

GROMACS Installation
--------------------

If GROMACS is not already installed, here's a quick installation guide. Our plugin has been tested with GROMACS ``v22.4``, ``v23.4`` and ``v24.2``, we suggest installation of one of these versions. GROMACS requires the latest version of cmake, you can download the relevant `cmake installer <https://cmake.org/download/>`_ and install this via the terminal with:

.. code-block:: bash

    bash cmake-3.30.2-linux-x86_64.sh

And include the path to cmake in the ``.bashrc`` file:

.. code-block:: bash

    export PATH="~/cmake-3.30.2-linux-x86_64.sh/bin:$PATH"

Download the relevant `GROMACS installer <https://manual.gromacs.org/documentation/>`_  and install via the `quick and dirty method <https://manual.gromacs.org/documentation/current/install-guide/index.html#>`_, summarised below:


Full GROMACS Installation
^^^^^^^^^^^^^^^^^^^^^^^^^

The full GROMACS intallation may take some time (approximately 1 hour),

.. code-block:: bash

    tar xfz gromacs-2022.4.tar.gz
    cd gromacs-2022.4
    mkdir build
    cd build
    cmake .. -DGMX_BUILD_OWN_FFTW=ON -DREGRESSIONTEST_DOWNLOAD=ON
    make
    make check
    sudo make install
    source /usr/local/gromacs/bin/GMXRC


Limited GROMACS Installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For a quicker, but limited GROMACS installation with OPENMP and MPI turned off, execute the following in the terminal:

.. code-block:: bash

    tar xfz gromacs-2022.4.tar.gz
    cd gromacs-2022.4
    mkdir build
    cd build
    cmake .. -DGMX_BUILD_OWN_FFTW=ON -DREGRESSIONTEST_DOWNLOAD=ON
    ccmake . # This will open a TUI, turn off OPENMP and THREAD_MPI, press 'c' to configure
    make -j16 # This will compile GROMACS with 16 threads, change this to the number of threads you have available
    sudo make install
    source /usr/local/gromacs/bin/GMXRC

Add the GROMACS path to the ``.bashrc`` file:

.. code-block:: bash

    export PATH=/usr/local/gromacs/bin:$PATH

To implement the changes to the ``.bashrc`` file, execute the following in the terminal:

.. code-block:: bash

    source ~/.bashrc

Check GROMACS is available in the terminal with:

.. code-block:: bash

    gmx -version

That is it. You have completed all the installation steps to record simulation data provenance for GROMACS.
