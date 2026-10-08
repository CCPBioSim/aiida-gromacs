=========================
Scripting with the Plugin
=========================

Before attempting to use the features here, you need to have completed the steps in :doc:`installation` and started the verdi daemon as described in :doc:`aiida_sessions`.

Using our plugin, it is possible to build powerful scripted workflows whilst capturing the provenance of data for each GROMACS step. The following documentation will show you how to use this plugin with a scripted interface so you can build it into your tools.

Data types
++++++++++

Currently there are a number of special considerations given to the data types that are provided as inputs into the calculation classes made available via this plugin.

**Code**

You will need to provide an AiiDA code object that will ultimately point to the real GROMACS install that you are going to use either on your system or via an HPC resource or similar. You can configure codes manually following steps outlined in the `AiiDA <https://aiida.readthedocs.io/projects/aiida-core/en/latest/howto/run_codes.html>`__ documentation, or you can use the helpers provided with the plugin to set this up for you, for example:

    .. code-block:: python

        # import the helper functions.
        from aiida_gromacs import helpers

        # First setup a computer, this will default to localhost (your pc).
        computer = helpers.get_computer()

        # Setup or grab a configured gromacs install.
        gromacs_code = helpers.get_code(entry_point='gromacs',
                                        computer=computer)

You can just use the above code if you are unsure how to set up this yourself and it will work. It relies on GROMACS being installed and available via the system path.

**Input Files**

Input files for each calculation are required to be marked as the AiiDA SinglefileData type, this is to make sure that the file is correctly added to the AiiDA file repository and its provenance tracked. You would do this by the flags for these, which will be added correctly by the calculation class and do not need to be specified as CLI parameters:

    .. code-block:: python

        # import AiiDA DataFactory and OS for paths
        from aiida.plugins import DataFactory
        import os

        # Instantiate the SingleFileData class
        SinglefileData = DataFactory('core.singlefile')

        # Now you can start mapping files.
        somefile = SinglefileData(file=os.path.join(os.getcwd(), 'some.file'))

**API Parameters and Outputs**

Flags for parameters setting properties or naming output files should be provided using the relevant Parameters data structures from the AiiDA DataFactory. An example of doing this is:

    .. code-block:: python

        # Import the DataFactory from AiiDA plugins.
        from aiida.plugins import DataFactory

        # Instantiate the data class for parameters, in this case we choose editconf as an example.
        # Doing this brings with it full validation for parameters based on the specific functionality.
        EditconfParameters = DataFactory('gromacs.editconf')

        # Now you can provide the commandline flags you would normally give to the gromacs executables.
        parameters = EditconfParameters({'center': '0',
                                        'd': '1.0',
                                        'bt': 'cubic',
                                        'o': '1AKI_newbox.gro'
                                        })

Please note, you do not need to provide input files to this parameters dictionary, since they have to be given special treatment so that provenance is properly tracked.

**Prepare data dict**

A main dictionary containing all of the input parameters to successfully run a calculation should be assembled with all of the required input fields data along with those given special AiiDA datatypes, otherwise you will see errors when submitting that things are missing. All of the different GROMACS applications covered within this plugin, will have three fields in common that should always be provided, these are:

#. code - this is an AiiDA code object
#. parameters - this is an AiiDA parameters object
#. metadata - this is dictionary containing metadata information

You should create this as a dictionary, for example:

    .. code-block:: python

        inputs = {
            'code': gromacs_code,
            'parameters': parameters,
            'metadata': {
                'description': 'this is a test example for documentation purposes',
            },
        }

Where the parameters 'gromacs_code' and 'parameters' are described above.

For each different gromacs executable that this plugin supports, there will then be a number of input files that you will need to specify.

Submit vs run
+++++++++++++

AiiDA has two main methods of execution in its engine that you can call for running your simulations. You should always make sure you are importing the engine from AiiDA to use these:

    .. code-block:: python

        from aiida import engine
        from aiida.plugins import CalculationFactory

The first method you can use to execute workloads is the run method:

    .. code-block:: python

        result = engine.run(CalculationFactory('gromacs.pdb2gmx'), **inputs)

This method is blocking, this means your script/program will be blocked from proceeding to the next step before the actual work done by the calculation is completed and any called programs or scripts have completed and exited. This is useful if your workflow is sequential and each step requires the previous step to have completed fully.

The second method you can use to execute is the submit method:

    .. code-block:: python

        result = engine.submit(CalculationFactory('gromacs.pdb2gmx'), **inputs)

This method is not blocking, which means that your workload is submitted to a running (you need to have started verdi daemons) daemon to execute and monitor and then your script is able to proceed forward without being blocked or waiting. This can be problematic if future steps rely on information from previous steps. You can monitor the progress of your submitted workloads via the verdi process commandline tools.

You should carefully consider which of the two execution methodologies are more appropriate based on the workflow you are writing tools for.

genericMD
+++++++++

The ``genericMD`` class is flexible, with no set required inputs or outputs, instead any number of inputs and outputs can be dynamically defined. Below is an example of using the ``genericMD`` class to run the equivalent of the ``gmx pdb2gmx`` command:

.. code-block:: python

    import os

    from aiida import engine, orm
    from aiida.plugins import CalculationFactory

    from aiida_gromacs import helpers

    # Computer and code object set up.
    computer = helpers.get_computer()
    gromacs_code = helpers.get_code(entry_point="gromacs", computer=computer)

    # input files used in pdb2gmx command
    inputs = ["1AKI_clean.pdb"]
    input_files = {}
    for filename in list(inputs):
        file_path = os.path.join(os.getcwd(), filename)
        input_files["pdbfile"] = orm.SinglefileData(file=file_path)

    # output files produced from pdb2gmx command
    output_files = [
        "1AKI_restraints.itp",
        "1AKI_topology.top",
        "1AKI_forcefield.gro",
    ]

    # full pdb2gmx command to run
    command = (
        "pdb2gmx -i 1AKI_restraints.itp "
        "-o 1AKI_forcefield.gro -p 1AKI_topology.top "
        "-ff oplsaa -water spce -f 1AKI_clean.pdb"
    )

    # set path to output dir
    output_dir = os.path.join(os.getcwd(), "outputs")


    # create input dictionary for calculation.
    process_inputs = {
        "code": gromacs_code,
        "command": orm.Str(command),
        "input_files": input_files,
        "output_files": orm.List(output_files),
        "metadata": {
            "label": "generic-execute",
            "description": "Run CLI job and save input and output file provenance.",
            "options": {
                "output_filename": "file.out",
                "output_dir": output_dir,
                "parser_name": "genericMD",
            },
        },
    }

    result = engine.run(CalculationFactory("genericMD"), **process_inputs)


editconf
++++++++

The ``editconf`` calculation class supports all parameters that the native gromacs application would use, you can find those `here <https://manual.gromacs.org/current/onlinehelp/gmx-editconf.html>`__. Here is an example of how to script calling the ``editconf`` class with examples from the Lemkul lysozyme tutorial.

Required input files:

* grofile

Required parameters:

* centre - shift geometrical centre
* d - distance from solute and box
* bt - box type
* o - output file name

.. code-block:: python

    from os import path
    from aiida import engine
    from aiida.plugins import CalculationFactory, DataFactory
    from aiida_gromacs import helpers

    # Get the GROMACS code object set up.
    computer = helpers.get_computer()
    gromacs_code = helpers.get_code(entry_point='gromacs',
                                    computer=computer)

    # Prepare input parameters these are generally any CLI flags and output files
    EditconfParameters = DataFactory('gromacs.editconf')
    parameters = EditconfParameters({'center': '0',
                                    'd': '1.0',
                                    'bt': 'cubic',
                                    'o': '1AKI_newbox.gro'
                                    })
    # Define input files as AiiDA SinglefileData.
    SinglefileData = DataFactory('core.singlefile')
    grofile = SinglefileData(file=path.join(os.getcwd(), '1AKI_forcefield.gro'))

    # Set up calculation dictionary
    inputs = {
        'code': gromacs_code,
        'parameters': parameters,
        'grofile': grofile,
        'metadata': {
            'description': 'editconf job submission with the aiida_gromacs plugin',
        },
    }

    # Run the calculation step in blocking mode.
    result = engine.run(CalculationFactory('gromacs.editconf'), **inputs)

genion
++++++

The ``genion`` calculation class supports all parameters that the native gromacs application would use, you can find those `here <https://manual.gromacs.org/current/onlinehelp/gmx-genion.html>`__

The ``genion`` class is slightly different in the way that the application being called underneath is bash and not gromacs directly, this is to satisfy the fact that ``gmx genion`` requires piped input for some parameters that cannot be given on the commandline.

Here is an example of how to script calling the ``genion`` class with examples from the Lemkul lysozyme tutorial.

Required input files:

* tprfile
* topfile

Required parameters:

* o - output file name
* pname - positive ion
* nname - negative ion
* neutral - neutralise charge

.. code-block:: python

    from os import path
    from aiida import engine
    from aiida.plugins import DataFactory, CalculationFactory
    from aiida_gromacs import helpers

    # Get the GROMACS code object set up.
    computer = helpers.get_computer()
    gromacs_code = helpers.get_code(entry_point='bash',
                                    computer=computer)

    # Prepare input parameters these are generally any CLI flags and output files
    GenionParameters = DataFactory('gromacs.genion')
    parameters = GenionParameters({'o': '1AKI_solvated_ions.gro',
                                   'pname': 'NA',
                                   'nname': 'CL',
                                   'neutral': 'true',
                                    })

    # Define input files as AiiDA SinglefileData.
    SinglefileData = DataFactory('core.singlefile')
    tprfile = SinglefileData(file=path.join(os.getcwd(), '1AKI_ions.tpr'))
    topfile = SinglefileData(file=path.join(os.getcwd(), '1AKI_topology.top'))

    # Set up calculation dictionary
    inputs = {
        'code': gromacs_code,
        'parameters': parameters,
        'tprfile': tprfile,
        'topfile': topfile,
        'metadata': {
            'description': 'genion job submission with the aiida_gromacs plugin',
        },
    }

    # Run the calculation step in blocking mode.
    result = engine.run(CalculationFactory('gromacs.genion'), **inputs)

grompp
++++++

The ``grompp`` calculation class supports all parameters that the native gromacs application would use, you can find those `here <https://manual.gromacs.org/current/onlinehelp/gmx-grompp.html>`__. Here is an example of how to script calling the ``grompp`` class with examples from the Lemkul lysozyme tutorial.

Required input files:

* mdpfile
* grofile
* topfile

Required parameters:

* o - output tpr file name

.. code-block:: python

    from os import path
    from aiida import engine
    from aiida.plugins import DataFactory, CalculationFactory
    from aiida_gromacs import helpers

    # Get the GROMACS code object set up.
    computer = helpers.get_computer()
    gromacs_code = helpers.get_code(entry_point='gromacs',
                                    computer=computer)

    # Prepare input parameters these are generally any CLI flags and output files
    GromppParameters = DataFactory('gromacs.grompp')
    parameters = GromppParameters({'o': '1AKI_ions.tpr'
                                    })

    # Define input files as AiiDA SinglefileData.
    SinglefileData = DataFactory('core.singlefile')
    mdpfile = SinglefileData(file=path.join(os.getcwd(), 'ions.mdp'))
    grofile = SinglefileData(file=path.join(os.getcwd(), '1AKI_solvated.gro'))
    topfile = SinglefileData(file=path.join(os.getcwd(), '1AKI_topology.top'))

    # Set up calculation dictionary
    inputs = {
        'code': gromacs_code,
        'parameters': parameters,
        'mdpfile': mdpfile,
        'grofile': grofile,
        'topfile': topfile,
        'metadata': {
            'description': 'grompp job submission with the aiida_gromacs plugin',
        },
    }

    # Run the calculation step in blocking mode.
    result = engine.run(CalculationFactory('gromacs.grompp'), **inputs)

mdrun
+++++

The ``mdrun`` calculation class supports all parameters that the native gromacs application would use, you can find those `here <https://manual.gromacs.org/current/onlinehelp/gmx-mdrun.html>`__. Here is an example of how to script calling the ``mdrun`` class with examples from the Lemkul lysozyme tutorial.

Required input files:

* tprfile

Required parameters:

* c - output structure file name
* e - output energy file name
* g - output log file name
* o - output trajectory file name

.. code-block:: python

    from os import path
    from aiida import engine
    from aiida.plugins import DataFactory, CalculationFactory
    from aiida_gromacs import helpers

    # Get the GROMACS code object set up.
    computer = helpers.get_computer()
    gromacs_code = helpers.get_code(entry_point='gromacs',
                                    computer=computer)

    # Prepare input parameters these are generally any CLI flags and output files
    MdrunParameters = DataFactory('gromacs.mdrun')
    parameters = MdrunParameters({'c': '1AKI_minimised.gro',
                                  'e': '1AKI_minimised.edr',
                                  'g': '1AKI_minimised.log',
                                  'o': '1AKI_minimised.trr',
                                  'v': 'true'
                                    })

    # Define input files as AiiDA SinglefileData.
    SinglefileData = DataFactory('core.singlefile')
    tprfile = SinglefileData(file=path.join(os.getcwd(), '1AKI_em.tpr'))

    # Set up calculation dictionary
    inputs = {
        'code': gromacs_code,
        'parameters': parameters,
        'tprfile': tprfile,
        'metadata': {
            'description': 'mdrun minimisation job submission with the aiida_gromacs plugin',
        },
    }

    # Run the calculation step in blocking mode.
    result = engine.run(CalculationFactory('gromacs.mdrun'), **inputs)

pdb2gmx
+++++++

The ``pdb2gmx`` calculation class supports all parameters that the native gromacs application would use, you can find those `here <https://manual.gromacs.org/current/onlinehelp/gmx-pdb2gmx.html>`__. Here is an example of how to script calling the ``pdb2gmx`` class with examples from the Lemkul lysozyme tutorial.

Required input files:

* pdbfile

Required parameters:

* ff - forcefield
* water - water model
* o - output file name
* p - topology file name
* i - itp file name

.. code-block:: python

    from os import path
    from aiida import engine
    from aiida.plugins import CalculationFactory, DataFactory
    from aiida_gromacs import helpers

    # Get the GROMACS code object set up.
    computer = helpers.get_computer()
    gromacs_code = helpers.get_code(entry_point='gromacs',
                                    computer=computer)

    # Prepare input parameters these are generally any CLI flags and output files
    Pdb2gmxParameters = DataFactory('gromacs.pdb2gmx')
    parameters = Pdb2gmxParameters({'ff': 'oplsaa',
                                    'water': 'spce',
                                    'o': '1AKI_forcefield.gro',
                                    'p': '1AKI_topology.top',
                                    'i': '1AKI_restraints.itp'
                                    })

    # Define input files as AiiDA SinglefileData.
    SinglefileData = DataFactory('core.singlefile')
    pdbfile = SinglefileData(file=path.join(os.getcwd(), '1AKI_clean.pdb'))

    # Set up calculation dictionary
    inputs = {
        'code': gromacs_code,
        'parameters': parameters,
        'pdbfile': pdbfile,
        'metadata': {
            'description': 'pdb2gmx job submission with the aiida_gromacs plugin',
        },
    }

    # Run the calculation step in blocking mode.
    result = engine.run(CalculationFactory('gromacs.pdb2gmx'), **inputs)

solvate
+++++++

The ``solvate`` calculation class supports all parameters that the native gromacs application would use, you can find those `here <https://manual.gromacs.org/current/onlinehelp/gmx-solvate.html>`__. Here is an example of how to script calling the ``solvate`` class with examples from the Lemkul lysozyme tutorial.

Required input files:

* grofile
* topfile

Required parameters:

* cs - water model
* o - output file name

.. code-block:: python

    from os import path
    from aiida import engine
    from aiida.plugins import DataFactory, CalculationFactory
    from aiida_gromacs import helpers

    # Get the GROMACS code object set up.
    computer = helpers.get_computer()
    gromacs_code = helpers.get_code(entry_point='gromacs',
                                    computer=computer)

    # Prepare input parameters these are generally any CLI flags and output files
    SolvateParameters = DataFactory('gromacs.solvate')
    parameters = SolvateParameters({'cs': 'spc216.gro',
                                    'o': '1AKI_solvated.gro'
                                    })

    # Define input files as AiiDA SinglefileData.
    SinglefileData = DataFactory('core.singlefile')
    grofile = SinglefileData(file=path.join(os.getcwd(), '1AKI_newbox.gro'))
    topfile = SinglefileData(file=path.join(os.getcwd(), '1AKI_topology.top'))

    # Set up calculation dictionary
    inputs = {
        'code': gromacs_code,
        'parameters': parameters,
        'grofile': grofile,
        'topfile': topfile,
        'metadata': {
            'description': 'solvate job submission with the aiida_gromacs plugin',
        },
    }

    # Run the calculation step in blocking mode.
    result = engine.run(CalculationFactory('gromacs.solvate'), **inputs)

make_ndx
++++++++

The ``make_ndx`` calculation class supports all parameters that the native gromacs application would use, you can find those `here <https://manual.gromacs.org/current/onlinehelp/gmx-make_ndx.html>`__. Here is an example of how to script calling the ``make_ndx`` class.

.. code-block:: python

    import os
    from aiida import cmdline, engine
    from aiida.plugins import CalculationFactory, DataFactory
    from aiida_gromacs import helpers

    # Get the GROMACS code object set up.
    computer = helpers.get_computer()
    gromacs_code = helpers.get_code(entry_point='gromacs',
                                    computer=computer)

    # Prepare input parameters these are generally any CLI flags and output files
    Make_ndxParameters = DataFactory("gromacs.make_ndx")
    parameters = Make_ndxParameters({'o': 'index.ndx'
                                    })

    # Define input files as AiiDA SinglefileData.
    SinglefileData = DataFactory('core.singlefile')
    grofile = SinglefileData(file=path.join(os.getcwd(), '1AKI_minimised.gro'))

    # Set up calculation dictionary
    inputs = {
        'code': gromacs_code,
        'parameters': parameters,
        'grofile': grofile,
        'metadata': {
            'description': 'make_ndx job submission with the aiida_gromacs plugin',
        },
    }

    # Run the calculation step in blocking mode.
    result = engine.run(CalculationFactory('gromacs.make_ndx'), **inputs)
