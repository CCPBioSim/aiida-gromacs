================
Start/Stop AiiDA
================

Regardless of whether you have switched off AiiDA or restarted your computer. To start recording provenance with this plugin, you will need to start up your AiiDA instance. Likewise, once you have finished using AiiDA, it is best practice to shut things down gracefully. These steps also assume you have already followed the steps within `installation <https://aiida-gromacs.readthedocs.io/en/latest/user_guide/installation.html>`_ and have already a fully working install of the toolchain.

The first step in starting AiiDA is to activate your conda environment, for example:

.. code-block:: bash

    conda activate aiida-gromacs-env

Starting AiiDA
--------------

The next step is to create an AiiDA profile:

.. code-block:: bash

    verdi presto --use-zeromq

Then start the AiiDA process daemon:

.. code-block:: bash

    verdi daemon start 2

You can then confirm all is well by checking the status of verdi:

.. code-block:: bash

    verdi status

Now, you are ready to start using AiiDA to track your GROMACS simulations.

Stopping AiiDA
--------------

It is best to stop your AiiDA instance gracefully than to simply close your VM or shutdown your computer, this protects against any issues that might corrupt your database.

Firstly stop the verdi process daemon:

.. code-block:: bash

    verdi daemon stop

Finally you can deactivate your conda environment:

.. code-block:: bash

    conda deactivate

That is it, you now have fully disabled the AiiDA toolchain.


Switching AiiDA Database Profile
--------------------------------

If you are working on multiple projects, you can create another profile with:

.. code-block:: bash

    verdi presto --use-zeromq

And view all created profiles:

.. code-block:: bash

    verdi profile list

If you want to switch to a different ``<PROFILE>``:

.. code-block:: bash

    verdi profile set-default <PROFILE>

And to delete a profile no longer needed:

.. code-block:: bash

    verdi profile delete <PROFILE>

You can now create, switch and delete profiles saved in the AiiDA database.
