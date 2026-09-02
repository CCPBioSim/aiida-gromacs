#!/usr/bin/env python
"""CLI utility to run gmx genion with AiiDA.

Usage: gmx_genion --help
"""

import os

import click
from aiida import cmdline, engine
from aiida.plugins import CalculationFactory, DataFactory

from aiida_gromacs import helpers
from aiida_gromacs.utils import searchprevious


def launch(params):
    """Run genion.

    Uses helpers to add gromacs on localhost to AiiDA on the fly.
    """

    # Prune unused CLI parameters from dict.
    params = {k: v for k, v in params.items() if v is not None}

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
        # inputs["code"] = helpers.get_code(entry_point="bash", computer=computer)

    # save the full command as a string in the inputs dict
    inputs = searchprevious.save_command("gmx genion", params, inputs)

    input_file_labels = {}  # dict used for finding previous nodes
    input_file_labels[params["s"]] = "tprfile"
    input_file_labels[params["p"]] = "topfile"
    SinglefileData = DataFactory("core.singlefile")
    if "instructions" in params:
        inputs["metadata"]["options"]["stdin_filename"] = str(params["instructions"])
        inputs["instructions_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("instructions")))
    else:
        # if no instructions given, then default to hard coded genion input
        inputs["code"] = helpers.get_code(entry_point="bash", computer=computer)

    # Prepare input parameters in AiiDA formats.
    inputs["tprfile"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("s")))
    inputs["topfile"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("p")))

    if "n" in params:
        inputs["n_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("n")))

    GenionParameters = DataFactory("gromacs.genion")
    inputs["parameters"] = GenionParameters(params)

    # check if inputs are outputs from prev processes
    inputs = searchprevious.link_previous_file_nodes(input_file_labels, inputs)

    # check if a pytest test is running, if so run rather than submit aiida job
    # Note: in order to submit your calculation to the aiida daemon, do:
    if "PYTEST_CURRENT_TEST" in os.environ:
        engine.run(CalculationFactory("gromacs.genion"), **inputs)
    else:
        engine.submit(CalculationFactory("gromacs.genion"), **inputs)


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
# Plugin options
@click.option(
    "--description",
    default="record genion data provenance via the aiida_gromacs plugin",
    type=str,
    help="Short metadata description",
)
# Input file options
@click.option("-s", default="topol.tpr", type=str, help="Input structure file")
@click.option("-n", type=str, help="Index file")
@click.option("-p", default="topol.top", type=str, help="Topology file")
@click.option(
    "--instructions",
    type=str,
    help="aiida-gromacs specific option: File containing interactive instructions for genion command, each "
    "instruction should be on a new line in the file.",
)
# Output file options
@click.option("-o", default="out.gro", type=str, help="Output structure file")
# Other parameter options
@click.option("-np", type=str, help="Number of positive ions")
@click.option("-pname", default="NA", type=str, help="Name of positive ion")
@click.option("-pq", type=str, help="Charge of the positive ion")
@click.option("-nn", type=str, help="Number of negative ions")
@click.option("-nname", default="CL", type=str, help="Name of negative ion")
@click.option("-nq", type=str, help="Charge of the negative ion")
@click.option("-rmin", type=str, help="Minimum distance between ions and non-solvent")
@click.option("-seed", type=str, help="Seed for random number generator (0 means generate)")
@click.option(
    "-conc",
    type=str,
    help="Specify salt concentration (mol/liter). This will add sufficient ions to reach up to the specified "
    "concentration as computed from the volume of the cell in the input .tpr file. Overrides the -np and -nn options.",
)
@click.option("-neutral", default="false", type=str, help="Neutralise the system with ions")
def cli(*args, **kwargs):
    """Run example.

    Example usage:

    $ gmx_genion --code gmx@localhost -s 1AKI_ions.tpr -p 1AKI_topology.top \
        -pname NA -nname CL -neutral true -o 1AKI_solvated_ions.gro \
        --instructions instructions.txt

    Alternative (automatically tried to create gmx@localhost code, but requires
    gromacs to be installed and available in your environment path):

    $ gmx_genion -s 1AKI_ions.tpr -p 1AKI_topology.top \
        -pname NA -nname CL -neutral true -o 1AKI_solvated_ions.gro \
        --instructions instuctions.txt

    Help: $ gmx_genion --help
    """

    launch(kwargs)


if __name__ == "__main__":
    cli()
