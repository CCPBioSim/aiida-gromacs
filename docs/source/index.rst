:html_theme.sidebar_secondary.remove:

aiida-gromacs
=============

.. ccpbiosim-hero::
   :logo-light: images/aiida-gromacs-logo.svg
   :logo-dark: images/aiida-gromacs-logo.svg
   :logo-alt: aiida-gromacs logo
   :tagline: aiida-gromacs
   :button: user_guide/index | Get started
   :github: CCPBioSim/aiida-gromacs

   AiiDA plugin that wraps Gromacs molecular dynamics executables

The Gromacs plugin for `AiiDA`_ captures and shares the full provenance of data
when parameterising and running molecular dynamics simulations.

Quick start
-----------

.. tab-set::

   .. tab-item:: pip

      .. code-block:: bash

         pip install aiida-gromacs

   .. tab-item:: Conda

      .. code-block:: bash

         conda install -c ccpbiosim aiida-gromacs

Explore the documentation
-------------------------

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: 🚀 User Guide
      :link: user_guide/index
      :link-type: doc

      Install aiida-gromacs and run Gromacs with AiiDA.

   .. grid-item-card:: 🎓 Tutorials
      :link: tutorials/index
      :link-type: doc

      Worked examples using aiida-gromacs.

   .. grid-item-card:: 👩‍💻 Developer Guide
      :link: developer_guide/index
      :link-type: doc

      Setting up a development environment and contributing.

   .. grid-item-card:: 📖 API
      :link: reference/aiida_gromacs/index
      :link-type: doc

      Reference for the aiida-gromacs package.

   .. grid-item-card:: 🌐 AiiDA Documentation
      :link: https://aiida.readthedocs.io

      The documentation for AiiDA itself.

.. toctree::
   :maxdepth: 2
   :hidden:

   User Guide <user_guide/index>
   Tutorials <tutorials/index>
   Developer Guide <developer_guide/index>
   API <reference/aiida_gromacs/index>
   AiiDA Documentation <https://aiida.readthedocs.io>

Citing
------

If you use this plugin for your research, please cite the following work:

.. highlights:: TBD, watch this space.

If you use AiiDA for your research, please cite the following work:

.. highlights:: Giovanni Pizzi, Andrea Cepellotti, Riccardo Sabatini, Nicola Marzari,
  and Boris Kozinsky, *AiiDA: automated interactive infrastructure and database
  for computational science*, Comp. Mat. Sci 111, 218-230 (2016);
  https://doi.org/10.1016/j.commatsci.2015.09.013; http://www.aiida.net.

``aiida-gromacs`` is released under the MIT license.

Contact
-------

Please contact Jas Kalayan jas.kalayan@stfc.ac.uk  or James Gebbie-Rayet james.gebbie@stfc.ac.uk for information concerning ``aiida-gromacs`` and the `AiiDA mailing list <http://www.aiida.net/mailing-list/>`_ for questions concerning ``aiida``.

Funding
-------

Contributors to aiida-gromacs were supported by

.. image::  images/psdi-logo.png
   :height: 100px
   :target: https://www.psdi.ac.uk/

.. image:: images/ccpbiosim-logo-white-background.png
   :height: 100px
   :target: https://www.ccpbiosim.org/

.. image:: images/cosec-logo.png
   :height: 100px
   :target: https://www.scd.stfc.ac.uk/Pages/CoSeC.aspx

.. _AiiDA: http://www.aiida.net
