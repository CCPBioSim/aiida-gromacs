#!/usr/bin/env python
"""CLI utility to run gmx editconf with AiiDA.

Usage: gmx_editconf --help
"""

import os

import click

from aiida import cmdline, engine, orm
from aiida.plugins import CalculationFactory, DataFactory

from aiida_gromacs import helpers
from aiida_gromacs.utils import searchprevious


def launch(params):
    """Run editconf.

    Uses helpers to add gromacs on localhost to AiiDA on the fly.
    """

    # Prune unused CLI parameters from dict.
    params = {k:v for k,v in params.items() if v != None}

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
    inputs = searchprevious.save_command("gmx editconf", params, inputs)

    input_file_labels = {} # dict used for finding previous nodes
    input_file_labels[params["f"]] = "grofile"

    # Prepare input parameters in AiiDA formats.
    SinglefileData = DataFactory("core.singlefile")
    inputs["grofile"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("f")))

    if "n" in params:
        inputs["n_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("n")))

    if "bf" in params:
        inputs["bf_file"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("bf")))

    EditconfParameters = DataFactory("gromacs.editconf")
    inputs["parameters"] = EditconfParameters(params)

    # check if inputs are outputs from prev processes
    inputs = searchprevious.link_previous_file_nodes(input_file_labels, inputs)

    # check if a pytest test is running, if so run rather than submit aiida job
    # Note: in order to submit your calculation to the aiida daemon, do:
    if "PYTEST_CURRENT_TEST" in os.environ:
        future = engine.run(CalculationFactory("gromacs.editconf"), **inputs)
    else:
        future = engine.submit(CalculationFactory("gromacs.editconf"), **inputs)


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
# Plugin options
@click.option("--description", default="record editconf data provenance via the aiida_gromacs plugin", type=str, help="Short metadata description")
# Input file options
@click.option("-f", default="conf.gro", type=str, help="Input structure file")
@click.option("-n", type=str, help="Index file")
@click.option("-bf", type=str, help="Generic data file")
# Output file options
@click.option("-o", default="out.gro", type=str, help="Output structure file")
@click.option("-mead", type=str, help="Coordination file for MEAD")
# Other parameter options
@click.option("-w", type=str, help="View output .xvg, .xpm, .eps and .pdb files")
@click.option("-ndef", type=str, help="Choose output from default index groups")
@click.option("-bt", default="triclinic", type=str, help="Box type")
@click.option("-box", type=str, help="Box vector lengths (a,b,c)")
@click.option("-angle", type=str, help="Angles between the box vectors (bc,ac,ab)")
@click.option("-d", default="0", type=str, help="Distance between box and solute")
@click.option("-c", type=str, help="Center molecule in box (implied by -box and -d)")
@click.option("-center", default="0 0 0", type=str, help="Shift geometrical center")
@click.option("-aligncenter", type=str, help="Center of rotation for alignment")
@click.option("-align", type=str, help="Align to target vector")
@click.option("-translate", type=str, help="Translation")
@click.option("-rotate", type=str, help="Rotation around the X, Y and Z axes in degrees")
@click.option("-princ", type=str, help="Orient molecule(s) along their principal axes")
@click.option("-scale", type=str, help="Scaling factor")
@click.option("-density", type=str, help="Density (g/L) of the output box achieved by scaling")
@click.option("-pbc", type=str, help="Remove the periodicity (make molecule whole again)")
@click.option("-resnr", type=str, help="Renumber residues starting from resnr")
@click.option("-grasp", type=str, help="Store the charge of the atom in the B-factor field and the radius of the atom in the occupancy field")
@click.option("-rvdw", type=str, help="Default Van der Waals radius (in nm) if one can not be found in the database or if no parameters are present in the topology file")
@click.option("-sig56", type=str, help="Use rmin/2 (minimum in the Van der Waals potential) rather than sigma/2")
@click.option("-vdwread", type=str, help="Read the Van der Waals radii from the file vdwradii.dat rather than computing the radii based on the force field")
@click.option("-atom", type=str, help="Force B-factor attachment per atom")
@click.option("-legend", type=str, help="Make B-factor legend")
@click.option("-label", type=str, help="Add chain label for all residues")
@click.option("-conect", type=str, help="Add CONECT records to a .pdb file when written. Can only be done when a topology is present")
def cli(*args, **kwargs):
    """Run example.

    Example usage:

    $ gmx_editconf --code gmx@localhost -f 1AKI_forcefield.gro -center 0 -d 1.0 -bt cubic -o 1AKI_newbox.gro

    Alternative (automatically tried to create gmx@localhost code, but requires
    gromacs to be installed and available in your environment path):

    $ gmx_editconf -f 1AKI_forcefield.gro -center 0 -d 1.0 -bt cubic -o 1AKI_newbox.gro

    Help: $ gmx_editconf --help
    """

    launch(kwargs)


if __name__ == "__main__":
    cli()
