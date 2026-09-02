#!/usr/bin/env python
"""CLI utility to run gmx make_ndx with AiiDA.

Usage: gmx_make_ndx --help
"""

import os
import click
from aiida import cmdline, engine
from aiida.plugins import CalculationFactory, DataFactory
from aiida_gromacs import helpers
from aiida_gromacs.utils import searchprevious


def launch(params):
    """Run make_ndx.

    Uses helpers to add gromacs on localhost to AiiDA on the fly.
    """

    # Prune unused CLI parameters from dict.
    params = {k:v for k,v in params.items() if v != None}

    # dict to hold our calculation data.
    inputs = {
        "metadata": {
            "description": params.pop("description"),
            "options": {},
        },
    }

    # If code is not initialised, then setup.
    if "code" in inputs:
        inputs["code"] = params.pop("code")
    else:
        computer = helpers.get_computer()
        inputs["code"] = helpers.get_code(entry_point="gromacs", computer=computer)

    # save the full command as a string in the inputs dict
    inputs = searchprevious.save_command("gmx make_ndx", params, inputs)

    # Prepare input parameters in AiiDA formats.
    SinglefileData = DataFactory("core.singlefile")

    input_file_labels = {} # dict used for finding previous nodes
    if "f" in params:
        input_file_labels[params["f"]] = "grofile"
        inputs["grofile"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("f")))
    if "n" in params:
        inputs["n_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("n")))
    if "instructions" in params:
        inputs["metadata"]["options"]["stdin_filename"] = str(params["instructions"])
        inputs["instructions_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("instructions")))

    Make_ndxParameters = DataFactory("gromacs.make_ndx")
    inputs["parameters"] = Make_ndxParameters(params)

    # check if inputs are outputs from prev gmx_* processes
    inputs = searchprevious.link_previous_file_nodes(input_file_labels, inputs)

    # check if a pytest test is running, if so run rather than submit aiida job
    # Note: in order to submit your calculation to the aiida daemon, do:
    if "PYTEST_CURRENT_TEST" in os.environ:
        future = engine.run(CalculationFactory("gromacs.make_ndx"), **inputs)
    else:
        future = engine.submit(CalculationFactory("gromacs.make_ndx"), **inputs)


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
# Plugin options
@click.option("--description", default="record make_ndx data provenance via the aiida_gromacs plugin", type=str, help="Short metadata description")
# Input file options
@click.option("-f", type=str, help="(Optional) Structure file: gro g96 pdb brk ent esp tpr")
@click.option("-n", type=str, help="(Optional) Index file")
@click.option("--instructions", type=str, help="aiida-gromacs specific option: File containing interactive instructions for make_ndx command, each instruction should be on a new line in the file.")
# Output file options
@click.option("-o", type=str, help="(Optional) Index file")
# Other parameters
@click.option("-natoms", type=str, help="set number of atoms (default: read from coordinate or index file)")
@click.option("-notwin", type=str, help="Duplicate all index groups with an offset of -natoms")
@click.option("-twin", type=str, help="Duplicate all index groups with an offset of -natoms")
def cli(*args, **kwargs):
    """Run example.

    Example usage:

    $ gmx_make_ndx --code gmx@localhost -f 1AKI_minimised.gro -o index.ndx --instructions inputs.txt

    Alternative (automatically tried to create gmx@localhost code, but requires
    gromacs to be installed and available in your environment path):

    $ gmx_make_ndx -f 1AKI_minimised.gro -o index.ndx --instructions inputs.txt 

    Help: $ gmx_make_ndx --help
    """

    launch(kwargs)


if __name__ == "__main__":
    cli()
