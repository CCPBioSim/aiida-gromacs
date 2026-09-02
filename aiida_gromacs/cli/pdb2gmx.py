#!/usr/bin/env python
"""CLI utility to run gmx pdb2gmx with AiiDA.

Usage: gmx_pdb2gmx --help
"""

import os
import sys
import click

from aiida import cmdline, engine, orm
from aiida.plugins import CalculationFactory, DataFactory

from aiida_gromacs import helpers
from aiida_gromacs.utils import searchprevious


def launch(params):
    """Run pdb2gmx.

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
    inputs = searchprevious.save_command("gmx pdb2gmx", params, inputs)

    input_file_labels = {} # dict used for finding previous nodes
    input_file_labels[params["f"]] = "pdbfile"

    # Prepare input parameters in AiiDA formats.
    SinglefileData = DataFactory("core.singlefile")
    inputs["pdbfile"] = SinglefileData(file=os.path.join(os.getcwd(), params.pop("f")))

    Pdb2gmxParameters = DataFactory("gromacs.pdb2gmx")
    inputs["parameters"] = Pdb2gmxParameters(params)

    # check if inputs are outputs from prev processes
    inputs = searchprevious.link_previous_file_nodes(input_file_labels, inputs)

    # check if a pytest test is running, if so run rather than submit aiida job
    # Note: in order to submit your calculation to the aiida daemon, do:
    if "PYTEST_CURRENT_TEST" in os.environ:
        future = engine.run(CalculationFactory("gromacs.pdb2gmx"), **inputs)
    else:
        future = engine.submit(CalculationFactory("gromacs.pdb2gmx"), **inputs)


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
# Plugin options
@click.option("--description", default="record pdb2gmx data provenance via the aiida_gromacs plugin", type=str, help="Short metadata description")
# Input file options
@click.option("-f", default="prot.pdb", type=str, help="Input structure file")
# Output file options 
@click.option("-o", default="conf.gro", type=str, help="Output structure file")
@click.option("-p", default="topol.top", type=str, help="Output topology file")
@click.option("-i", default="posre.itp", type=str, help="Output itp file")
@click.option("-n", type=str, help="Output index file")
@click.option("-q", type=str, help="Output Structure file")
# Parameter options
@click.option("-chainsep", type=str, help="Condition in PDB files when a new chain should be started (adding termini): id_or_ter, id_and_ter, ter, id, interactive")
@click.option("-merge", type=str, help="Merge multiple chains into a single [moleculetype]: no, all, interactive")
@click.option("-ff", required=True, type=str, help="Forcefield")
@click.option("-water", required=True, type=str, help="Water model")

@click.option("-inter", type=str, help="Set the next 8 options to interactive")
@click.option("-ss", type=str, help="Interactive SS bridge selection")
@click.option("-ter", type=str, help="Interactive termini selection, instead of charged (default)")
@click.option("-lys", type=str, help="Interactive lysine selection, instead of charged")
@click.option("-arg", type=str, help="Interactive arginine selection, instead of charged")
@click.option("-asp", type=str, help="Interactive aspartic acid selection, instead of charged")
@click.option("-glu", type=str, help="Interactive glutamic acid selection, instead of charged")
@click.option("-gln", type=str, help="Interactive glutamine selection, instead of charged")
@click.option("-his", type=str, help="Interactive histidine selection, instead of checking H-bonds")
@click.option("-angle", type=str, help="Minimum hydrogen-donor-acceptor angle for a H-bond (degrees)")
@click.option("-dist", type=str, help="Maximum donor-acceptor distance for a H-bond (nm)")
@click.option("-una", type=str, help="Select aromatic rings with united CH atoms on phenylalanine, tryptophane and tyrosine")
@click.option("-ignh", type=str, help="Ignore hydrogen atoms that are in the coordinate file")
@click.option("-missing", type=str, help="Continue when atoms are missing and bonds cannot be made, dangerous")
@click.option("-v", type=str, help="Force constant for position restraints")
@click.option("-posrefc", type=str, help="Force constant for position restraints")
@click.option("-vsite", type=str, help="Convert atoms to virtual sites: none, hydrogens, aromatics")
@click.option("-heavyh", type=str, help="Make hydrogen atoms heavy")
@click.option("-deuterate", type=str, help="Change the mass of hydrogens to 2 amu")
@click.option("-chargegrp", type=str, help="Use charge groups in the .rtp file")
@click.option("-cmap", type=str, help="Use cmap torsions (if enabled in the .rtp file)")
@click.option("-renum", type=str, help="Renumber the residues consecutively in the output")
@click.option("-rtpres", type=str, help="Use .rtp entry names as residue names")
def cli(*args, **kwargs):
    """Run example.

    Example usage:

    $ gmx_pdb2gmx --code gmx@localhost -f 1AKI_clean.pdb -ff oplsaa -water spce -o 1AKI_forcefield.gro -p 1AKI_topology.top -i 1AKI_restraints.itp

    Alternative (automatically tried to create gmx@localhost code, but requires
    gromacs to be installed and available in your environment path):

    $ gmx_pdb2gmx -f 1AKI_clean.pdb -ff oplsaa -water spce -o 1AKI_forcefield.gro -p 1AKI_topology.top -i 1AKI_restraints.itp

    Help: $ gmx_pdb2gmx --help
    """

    launch(kwargs)


if __name__ == "__main__":
    cli()
