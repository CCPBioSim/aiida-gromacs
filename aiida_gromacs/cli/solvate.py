#!/usr/bin/env python
"""CLI utility to run gmx solvate with AiiDA.

Usage: gmx_solvate --help
"""

import os

import click
from aiida import cmdline, engine
from aiida.plugins import CalculationFactory, DataFactory

from aiida_gromacs import helpers
from aiida_gromacs.utils import searchprevious


def launch(params):
    """Run solvate.

    Uses helpers to add gromacs on localhost to AiiDA on the fly.
    """

    # Prune unused CLI parameters from dict.
    params = {k: v for k, v in params.items() if v is not None}

    # dict to hold our calculation data.
    inputs = {
        "metadata": {
            "description": params.pop("description"),
        },
    }

    # If code is not initialised, then setup.
    if "code" in inputs:
        inputs["code"] = params.pop("code")
    else:
        computer = helpers.get_computer()
        inputs["code"] = helpers.get_code(entry_point="gromacs", computer=computer)

    # save the full command as a string in the inputs dict
    inputs = searchprevious.save_command("gmx solvate", params, inputs)

    input_file_labels = {}  # dict used for finding previous nodes
    input_file_labels[params["cp"]] = "grofile"
    input_file_labels[params["p"]] = "topfile"

    # Prepare input parameters in AiiDA formats.
    SinglefileData = DataFactory("core.singlefile")
    inputs["grofile"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("cp")))
    inputs["topfile"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("p")))

    if "cs" in params:
        if params["cs"] != "spc216.gro":  # needs fixing
            inputs["cs_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("cs")))

    SolvateParameters = DataFactory("gromacs.solvate")
    inputs["parameters"] = SolvateParameters(params)

    # check if inputs are outputs from prev processes
    inputs = searchprevious.link_previous_file_nodes(input_file_labels, inputs)

    # check if a pytest test is running, if so run rather than submit aiida job
    # Note: in order to submit your calculation to the aiida daemon, do:
    if "PYTEST_CURRENT_TEST" in os.environ:
        engine.run(CalculationFactory("gromacs.solvate"), **inputs)
    else:
        engine.submit(CalculationFactory("gromacs.solvate"), **inputs)


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
# Plugin options
@click.option(
    "--description",
    default="record solvate data provenance via the aiida_gromacs plugin",
    type=str,
    help="Short metadata description",
)
# Input file options
@click.option("-cp", default="protein.gro", type=str, help="Input structure file")
@click.option("-cs", default="spc216.gro", type=str, help="Library structure file")
@click.option("-p", default="topol.top", type=str, help="Topology file")
# Output file options
@click.option("-o", default="out.gro", type=str, help="Output structure file")
# Other parameter options
@click.option("-box", type=str, help="Box size (in nm)")
@click.option("-radius", type=str, help="Default van der Waals distance")
@click.option(
    "-scale",
    type=str,
    help="Scale factor to multiply Van der Waals radii from the database in share/gromacs/top/vdwradii.dat. "
    "The default value of 0.57 yields density close to 1000 g/l for proteins in water.",
)
@click.option("-shell", type=str, help="Thickness of optional water layer around solute")
@click.option(
    "-maxsol",
    type=str,
    help="Maximum number of solvent molecules to add if they fit in the box. If zero (default) this is ignored",
)
@click.option("-vel", type=str, help="Keep velocities from input solute and solvent")
def cli(*args, **kwargs):
    """Run example.

    Example usage:

    $ gmx_solvate --code gmx@localhost -cp 1AKI_newbox.gro -cs spc216.gro -p 1AKI_topology.top -o 1AKI_solvated.gro

    Alternative (automatically tried to create gmx@localhost code, but requires
    gromacs to be installed and available in your environment path):

    $ gmx_solvate -cp 1AKI_newbox.gro -cs spc216.gro -p 1AKI_topology.top -o 1AKI_solvated.gro

    Help: $ gmx_solvate --help
    """

    launch(kwargs)


if __name__ == "__main__":
    cli()
